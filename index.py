import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import re

def search_detik_articles(search_query, max_pages=2):
    """Mencari artikel di Detik.com berdasarkan query"""
    base_url = "https://www.detik.com/search/searchall?query="
    query = quote(search_query)
    
    articles_list = []
    
    for page in range(1, max_pages + 1):
        url = f"{base_url}{query}&page={page}"
        print(f"Mencari di halaman {page}...")
        
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error: {e}")
            continue
            
        soup = BeautifulSoup(response.text, "html.parser")

        article_links = soup.select("a[href*='/berita/'], a[href*='/news/']")
        
        for link in article_links:
            href = link.get('href', '')
            title = link.get_text(strip=True)

            if href and title and len(title) > 20 and '/berita/' in href:
                full_url = urljoin("https://www.detik.com", href)

                if not any(art['url'] == full_url for art in articles_list):
                    articles_list.append({
                        'title': title,
                        'url': full_url
                    })
        
        if not article_links:
            break
            
    return articles_list

def scrape_article_detail(article_url):
    """Scrape detail artikel dari URL tertentu"""
    try:
        print(f"\nMengambil detail dari: {article_url}")
        
        response = requests.get(article_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        title = soup.find('h1', class_='detail__title')
        title = title.get_text(strip=True) if title else "Judul tidak ditemukan"

        author = soup.find('div', class_='detail__author')
        author = author.get_text(strip=True) if author else "Penulis tidak ditemukan"
        
        date = soup.find('div', class_='detail__date')
        date = date.get_text(strip=True) if date else "Tanggal tidak ditemukan"

        image = soup.find('img', class_='p_img_zoomin')
        image_url = image['src'] if image and image.has_attr('src') else "Gambar tidak ditemukan"

        if image_url != "Gambar tidak ditemukan" and '?' in image_url:
            image_url = image_url.split('?')[0]
        
        content_div = soup.find('div', class_='detail__body-text')
        content = ""
        if content_div:
            paragraphs = content_div.find_all('p')
            content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        tags = []
        tags_div = soup.find('div', class_='detail__body-tag')
        if tags_div:
            tag_links = tags_div.find_all('a', class_='nav__item')
            tags = [tag.get_text(strip=True) for tag in tag_links]
        
        return {
            'title': title,
            'author': author,
            'date': date,
            'image_url': image_url,
            'content': content,
            'tags': tags,
            'url': article_url
        }
        
    except Exception as e:
        print(f"Error scraping article: {e}")
        return None

def main():
    """Program utama"""
    print("=" * 50)
    print("SCRAPER BERITA DETIK.COM")
    print("=" * 50)

    search_topic = input("Masukkan topik berita yang ingin dicari: ").strip()
    
    if not search_topic:
        print("Topik tidak boleh kosong!")
        return
    
    print(f"\nMencari berita tentang: {search_topic}")

    articles = search_detik_articles(search_topic)
    
    if not articles:
        print("Tidak ditemukan artikel untuk topik tersebut.")
        return

    print(f"\nDitemukan {len(articles)} artikel:")
    print("-" * 50)
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   URL: {article['url']}")
        print()
    
    # Pilih artikel
    try:
        choice = int(input(f"Pilih nomor artikel (1-{len(articles)}): "))
        if choice < 1 or choice > len(articles):
            print("Pilihan tidak valid!")
            return
            
        selected_article = articles[choice - 1]

        article_detail = scrape_article_detail(selected_article['url'])
        
        if article_detail:
            print("\n" + "=" * 50)
            print("HASIL SCRAPING:")
            print("=" * 50)
            print(f"Judul: {article_detail['title']}")
            print(f"Penulis: {article_detail['author']}")
            print(f"Tanggal: {article_detail['date']}")
            print(f"Gambar: {article_detail['image_url']}")
            print(f"Tags: {', '.join(article_detail['tags']) if article_detail['tags'] else 'Tidak ada tags'}")
            print(f"URL: {article_detail['url']}")
            print("\nKonten:")
            print("-" * 30)
            print(article_detail['content'][:500] + "..." if len(article_detail['content']) > 500 else article_detail['content'])
            
            save = input("\nSimpan hasil ke file? (y/n): ").lower()
            if save == 'y':
                filename = f"berita_{search_topic.lower().replace(' ', '_')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Judul: {article_detail['title']}\n")
                    f.write(f"Penulis: {article_detail['author']}\n")
                    f.write(f"Tanggal: {article_detail['date']}\n")
                    f.write(f"Gambar: {article_detail['image_url']}\n")
                    f.write(f"Tags: {', '.join(article_detail['tags'])}\n")
                    f.write(f"URL: {article_detail['url']}\n")
                    f.write("\nKonten:\n")
                    f.write(article_detail['content'])
                print(f"Hasil disimpan ke: {filename}")
                
    except ValueError:
        print("Masukkan angka yang valid!")
    except Exception as e:
        print(f"Terjadi error: {e}")

if __name__ == "__main__":
    main()