import requests
from bs4 import BeautifulSoup
import os

def main():
    url = "https://www.gutenberg.org/browse/scores/top"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        return
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the section with id 'books-last1' (Top 100 EBooks yesterday)
    top_100_header = soup.find('h2', id='books-last1')
    if not top_100_header:
        print("Could not find the Top 100 EBooks yesterday section")
        return
    ol = top_100_header.find_next_sibling('ol')
    if not ol:
        print("Could not find the list of top 100 books")
        return

    books = ol.find_all('li')
    print(f"Found {len(books)} books.")

    # Ensure the "books" directory exists
    if not os.path.exists('books'):
        os.makedirs('books')

    for i, book in enumerate(books[:100]):
        link = book.find('a')
        if not link:
            continue
        book_url = link['href']
        book_title = link.text
        # Extract the book number from the URL
        # The URL is of the form "/ebooks/84"
        book_number = book_url.strip('/').split('/')[-1]
        print(f"Processing book {i+1}: {book_title} (ID: {book_number})")

        # Construct the text file URL
        # Try the common pattern
        txt_url = f"https://www.gutenberg.org/cache/epub/{book_number}/pg{book_number}.txt"

        # Download the text file
        print(f"Attempting to download from {txt_url}")
        response = requests.get(txt_url)
        if response.status_code != 200:
            # Try alternative URL patterns if the first one fails
            txt_url = f"https://www.gutenberg.org/files/{book_number}/{book_number}-0.txt"
            print(f"Attempting to download from {txt_url}")
            response = requests.get(txt_url)
            if response.status_code != 200:
                txt_url = f"https://www.gutenberg.org/files/{book_number}/{book_number}.txt"
                print(f"Attempting to download from {txt_url}")
                response = requests.get(txt_url)
                if response.status_code != 200:
                    print(f"Failed to download text file for book {book_number}")
                    continue

        # Save the file
        # Clean up the book title for filename
        safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '_', '-')).rstrip()
        filename = os.path.join('books', f"{safe_title} - {book_number}.txt")
        # Ensure the filename is unique and safe
        # filename = filename.replace('/', '_')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved to {filename}")

if __name__ == "__main__":
    main()
