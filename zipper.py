import os
import zipfile

def zip_directory(folder_path, zip_path, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = []
        
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            # Exclude unwanted directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # Exclude specific heavy files if needed
                if file.endswith('.zip') or file.endswith('.pyc'):
                    continue
                    
                file_path = os.path.join(root, file)
                # Ensure we don't zip the zip file itself if it's inside the folder
                if file_path == zip_path:
                    continue
                    
                arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                zipf.write(file_path, arcname)
    print(f"Berhasil membuat: {zip_path}")

if __name__ == "__main__":
    base_dir = r"d:\College\KP"
    
    backend_src = os.path.join(base_dir, "Backend")
    backend_zip = os.path.join(base_dir, "backend.zip")
    
    scraper_src = os.path.join(base_dir, "Scrapers")
    scraper_zip = os.path.join(base_dir, "scraper.zip")
    
    # Exclude virtual environments, pycache, and massive raw data
    excludes = ['.venv', 'venv', '__pycache__', 'raw_batches', '.git']
    
    if os.path.exists(backend_src):
        print(f"Zipping {backend_src}...")
        zip_directory(backend_src, backend_zip, excludes)
    else:
        print(f"Folder tidak ditemukan: {backend_src}")
        
    if os.path.exists(scraper_src):
        print(f"Zipping {scraper_src}...")
        zip_directory(scraper_src, scraper_zip, excludes)
    else:
        print(f"Folder tidak ditemukan: {scraper_src}")

print("Selesai!")
