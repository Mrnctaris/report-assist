import TkEasyGUI as sg
import requests
from bs4 import BeautifulSoup
import pdfplumber
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor

# テキスト要約関数
def summarize_text(text):
    print("要約処理開始")
    auto_abstractor = AutoAbstractor()
    auto_abstractor.tokenizable_doc = SimpleTokenizer()
    abstractor = TopNRankAbstractor()

    try:
        result_dict = auto_abstractor.summarize(text, abstractor)
        summary = '\n'.join(result_dict["summarize_result"])
        print("要約完了:", summary)
        return summary if summary else "要約できませんでした。"
    except Exception as e:
        print("要約中にエラー:", e)
        return "要約できませんでした。"

# PDFからテキストを抽出
def extract_text_from_pdf(pdf_path):
    print("PDF解析開始:", pdf_path)
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "  # 改行をスペースに変換
        cleaned_text = " ".join(text.split())  # 余分な空白を削除

        # コンソールに出力（デバッグ用）
        print("PDF本文の一部:", cleaned_text[:1000])  # 最初の1000文字を表示

        return cleaned_text if cleaned_text else "PDFからテキストを取得できませんでした。"
    except Exception as e:
        print("PDF解析エラー:", e)
        return "PDFを読み取れませんでした。"



# Web記事からテキストを取得
def fetch_web_text(url):
    print("Web取得開始:", url)
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')

        # 記事本文らしきテキストを取得
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
        else:
            paragraphs = soup.find_all('p')

        text = '\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])  # 20文字以上の段落を取得
        print("取得したWeb記事の全文:", text[:500])

        return text if text else "Web記事のテキストを取得できませんでした。"
    except Exception as e:
        print("Web取得エラー:", e)
        return "Web記事を取得できませんでした。"

# GUIメイン処理
def main():
    layout = [
        [sg.Text('Web記事のURL:'), sg.InputText(key='url'), sg.Button('取得')],
        [sg.Text('PDFファイル:'), sg.InputText(key='pdf_path'), sg.FileBrowse(file_types=(('PDF Files', '*.pdf'),))],
        [sg.Button('要約')],
        [sg.Text('タイトルリスト:')],
        [sg.Listbox(values=[], size=(50, 10), key='title_list')],
        [sg.Text('要約結果:')],
        [sg.Multiline(size=(60, 10), key='summary')],
    ]
    
    window = sg.Window('論文・記事要約ツール', layout)

    title_list = []

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        
        if event == '取得':
            url = values.get('url', '').strip()
            if url:
                text = fetch_web_text(url)
                if "取得できませんでした" in text:
                    window['summary'].update(text)
                    continue  # エラーならスキップ
                
                summary = summarize_text(text)
                print("GUIに表示する要約:", summary)

                window['summary'].update(summary)
                window.refresh()

                title_list.append(url)
                window['title_list'].update(title_list)
                
        if event == '要約':
            pdf_path = values.get('pdf_path', '').strip()
            if pdf_path:
                text = extract_text_from_pdf(pdf_path)
                if "取得できませんでした" in text:
                    window['summary'].update(text)
                    continue  # エラーならスキップ

                summary = summarize_text(text)
                print("GUIに表示する要約:", summary)

                window['summary'].update(summary)
                window.refresh()

                title_list.append(pdf_path)
                window['title_list'].update(title_list)
    
    window.close()

if __name__ == "__main__":
    main()
