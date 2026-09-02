import os
import sys
import json
import logging
import time
from datetime import datetime

# Setup path agar bisa import dari parent dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from libs.beans import Worker
from libs.cloud_storage import datalake
from settings import BEANS
from scrapers.receiver_server import find_posts_in_json, find_tiktok_posts_in_json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ParserWorker')

DATA_TUBE_IG = 'instagram_data_queue'
DATA_TUBE_TIKTOK = 'tiktok_data_queue'

def parse_instagram_post(node):
    """
    Ekstrak field penting dari raw JSON Instagram menjadi format standar.
    """
    try:
        # Variasi GraphQL yang berbeda
        shortcode = node.get('shortcode') or node.get('code')
        if not shortcode: return None
        
        # Ekstrak caption
        caption = ""
        try:
            edges = node.get('edge_media_to_caption', {}).get('edges', [])
            if edges and len(edges) > 0:
                caption = edges[0].get('node', {}).get('text', '')
            elif 'caption' in node:
                caption = node.get('caption', {}).get('text', '') or str(node.get('caption', ''))
        except: pass

        # Ekstrak owner/author
        owner = node.get('owner') or node.get('user') or {}
        author_username = owner.get('username', '')
        
        # Ekstrak metrik
        likes = node.get('edge_media_preview_like', {}).get('count') or node.get('like_count') or 0
        comments = node.get('edge_media_to_comment', {}).get('count') or node.get('comment_count') or 0
        views = node.get('video_view_count') or node.get('play_count') or 0
        timestamp = node.get('taken_at_timestamp') or node.get('taken_at') or int(time.time())
        
        return {
            "platform": "instagram",
            "post_id": shortcode,
            "author_username": author_username,
            "caption": caption,
            "metrics": {
                "likes": likes,
                "comments": comments,
                "views": views
            },
            "timestamp": timestamp,
            "url": f"https://www.instagram.com/p/{shortcode}/",
            "parsed_at": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error parsing IG node: {e}")
        return None

def parse_tiktok_post(aweme):
    """
    Ekstrak field penting dari raw JSON TikTok menjadi format standar.
    """
    try:
        video_id = aweme.get('aweme_id') or aweme.get('id')
        if not video_id: return None
        
        caption = aweme.get('desc', '')
        
        author = aweme.get('author', {})
        author_username = author.get('unique_id') or author.get('uid', '')
        
        stats = aweme.get('statistics', {}) or aweme.get('stats', {})
        likes = stats.get('digg_count') or stats.get('likeCount') or 0
        comments = stats.get('comment_count') or stats.get('commentCount') or 0
        views = stats.get('play_count') or stats.get('playCount') or 0
        shares = stats.get('share_count') or stats.get('shareCount') or 0
        
        timestamp = aweme.get('create_time') or int(time.time())
        
        return {
            "platform": "tiktok",
            "post_id": str(video_id),
            "author_username": author_username,
            "caption": caption,
            "metrics": {
                "likes": likes,
                "comments": comments,
                "views": views,
                "shares": shares
            },
            "timestamp": timestamp,
            "url": f"https://www.tiktok.com/@{author_username}/video/{video_id}",
            "parsed_at": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error parsing TikTok aweme: {e}")
        return None

def process_job(job_body):
    """
    Memproses satu job dari Beanstalkd (mengurai file batch, ekstrak, upload).
    """
    try:
        data = json.loads(job_body)
        file_name = data.get('path')
        platform = data.get('platform')
        
        from settings import PATH
        file_path = os.path.join(PATH['default']['rawpath'], file_name)
        
        if not file_name or not os.path.exists(file_path):
            logger.error(f"File tidak ditemukan: {file_path}")
            return True # Delete job so it doesn't stuck
            
        logger.info(f"Membuka file {platform} batch: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            batch_json = json.load(f)
            
        parsed_results = []
        
        # Ekstrak node per platform
        if platform == 'instagram':
            nodes = find_posts_in_json(batch_json)
            for node in nodes:
                parsed = parse_instagram_post(node)
                if parsed: parsed_results.append(parsed)
                
        elif platform == 'tiktok':
            nodes = find_tiktok_posts_in_json(batch_json)
            for node in nodes:
                parsed = parse_tiktok_post(node)
                if parsed: parsed_results.append(parsed)
        
        logger.info(f"Berhasil parse {len(parsed_results)} posts dari batch.")
        
        # Upload ke Data Lake
        month_folder = datetime.now().strftime("%Y-%m")
        for p in parsed_results:
            pid = p['post_id']
            filename = f"{platform}_{pid}.json"
            folder_path = f"{platform}/parsed/{month_folder}/"
            
            # Upload via cloud_storage.py
            datalake.upload_json(p, folder_path, filename)
            
        # Opsi: Hapus file raw lokal jika sudah sukses di-parse (untuk hemat disk)
        # os.remove(file_path)
            
        return True # Sukses, hapus job dari queue
        
    except Exception as e:
        logger.error(f"Gagal memproses job: {e}")
        return False # Biarkan job di queue (Release)

def run_worker():
    host = BEANS['default']['host']
    port = BEANS['default']['port']
    
    logger.info(f"🚀 Memulai Parser Worker, listen di {host}:{port}")
    logger.info(f"Tubes: {DATA_TUBE_IG}, {DATA_TUBE_TIKTOK}")
    
    # Inisiasi listener ke dua tube sekaligus menggunakan Worker class dari NoLimit
    worker = Worker([DATA_TUBE_IG, DATA_TUBE_TIKTOK], host=host, port=port)
    
    while True:
        try:
            job = worker.getJob()
            if job:
                success = process_job(job.body)
                if success:
                    job.delete()
                else:
                    job.release(delay=60) # Coba lagi 1 menit kemudian jika gagal (misal koneksi S3 putus)
            else:
                time.sleep(1) # Tunggu job baru
        except KeyboardInterrupt:
            logger.info("Worker dihentikan.")
            break
        except Exception as e:
            logger.error(f"Worker Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    run_worker()
