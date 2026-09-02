import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Konfigurasi Path agar bisa impor module Project
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from libs.general import store_raw
from libs.beans import Pusher
from settings import BEANS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Sembunyikan log Flask
logging.getLogger('werkzeug').setLevel(logging.WARNING)

app = Flask(__name__)
CORS(app)  # Izinkan ekstensi Chrome untuk mengirim data ke localhost

DATA_TUBE_IG = 'instagram_data_queue'
DATA_TUBE_TIKTOK = 'tiktok_data_queue'
seen_shortcodes = set()
posts_collected = 0

# Inisialisasi Producer Beanstalkd
try:
    host = BEANS['default']['host']
    port = BEANS['default']['port']
    producer_ig = Pusher(DATA_TUBE_IG, host=host, port=port)
    producer_tiktok = Pusher(DATA_TUBE_TIKTOK, host=host, port=port)
    logging.info(f"Terhubung ke Beanstalkd (IG: {DATA_TUBE_IG}, TikTok: {DATA_TUBE_TIKTOK}) di {host}:{port}")
except Exception as e:
    producer_ig = None
    producer_tiktok = None
    logging.error(f"Gagal konek Beanstalkd: {e}. Data tetap akan disimpan ke disk.")

def find_posts_in_json(data):
    """
    Fungsi rekursif untuk mencari post dari berbagai macam bentuk response GraphQL IG.
    Kita perlu membuatnya lebih agresif / pintar.
    """
    found = []
    if isinstance(data, dict):
        # Struktur IG lama (shortcode dan owner sejajar)
        if ('shortcode' in data and 'owner' in data) or ('code' in data and 'caption' in data and 'user' in data):
            found.append(data)
        # Struktur IG 2024 (node -> shortcode)
        elif 'node' in data and isinstance(data['node'], dict) and 'shortcode' in data['node']:
            found.append(data['node'])
        else:
            for k, v in data.items():
                found.extend(find_posts_in_json(v))
    elif isinstance(data, list):
        for item in data:
            found.extend(find_posts_in_json(item))
    return found

def find_tiktok_posts_in_json(data):
    """
    Fungsi rekursif untuk mencari data postingan TikTok (aweme).
    """
    found = []
    if isinstance(data, dict):
        # Struktur TikTok (biasanya memiliki 'aweme_id' atau 'id' beserta 'desc' atau 'author')
        if ('aweme_id' in data and 'desc' in data) or ('id' in data and 'desc' in data and 'author' in data):
            found.append(data)
        else:
            for k, v in data.items():
                found.extend(find_tiktok_posts_in_json(v))
    elif isinstance(data, list):
        for item in data:
            found.extend(find_tiktok_posts_in_json(item))
    return found


def process_batch(json_data, platform, num_posts):
    global posts_collected
    try:
        # Simpan raw data (satu batch utuh) ke Data Lake
        fname = store_raw(json_data, prefix=f'{platform}-batch', platform=platform, type='batch', posts_count=num_posts)
        
        posts_collected += num_posts
        logging.info(f"✅ [Total: {posts_collected}] Dapat BATCH {platform} ({num_posts} post) -> {fname}")
        
        # Kirim PATH file-nya ke Beanstalkd
        active_producer = producer_ig if platform == 'instagram' else producer_tiktok
        if active_producer:
            job_msg = {
                "path": fname,
                "platform": platform,
                "status": "raw_collected_batch"
            }
            active_producer.setJob(json.dumps(job_msg))
            
    except Exception as e:
        logging.error(f"Gagal memproses batch {platform}: {e}")

# (Fungsi individual dihapus, sekarang menggunakan process_batch)

@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.json
    if not data or 'body' not in data:
        return jsonify({"status": "error", "message": "Invalid payload"}), 400

    url = data.get('url', 'unknown')
    origin = data.get('origin', '')
    raw_body = data.get('body', '{}')

    try:
        # Ekstrak string JSON yang dikirimkan oleh browser
        json_data = json.loads(raw_body)
            
        tiktok_posts = find_tiktok_posts_in_json(json_data)
        ig_posts = find_posts_in_json(json_data)
        
        if len(tiktok_posts) > 0:
            process_batch(json_data, 'tiktok', len(tiktok_posts))
            return jsonify({"status": "success", "posts_found": len(tiktok_posts), "platform": "tiktok"})
            
        elif len(ig_posts) > 0:
            process_batch(json_data, 'instagram', len(ig_posts))
            return jsonify({"status": "success", "posts_found": len(ig_posts), "platform": "instagram"})
            
        return jsonify({"status": "ignored", "message": "No posts found"})

    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON in body"}), 400
    except Exception as e:
        logging.error(f"Error processing payload: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    logging.info("==================================================")
    logging.info("🚀 Narative Receiver Server BERJALAN di Port 5000")
    logging.info("Menunggu data dari Chrome Extension...")
    logging.info("==================================================")
    app.run(host='0.0.0.0', port=5000)
