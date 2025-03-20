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

        #  コンソールに出力（デバッグ用）
        print("PDF本文の一部:", cleaned_text[:1000])  # 最初の1000文字を表示

        return cleaned_text if cleaned_text else "PDFからテキストを取得できませんでした。"
    except Exception as e:
        print("PDF解析エラー:", e)
        return "PDFを読み取れませんでした。"




# Web記事からテキストを取得
def extract_text_from_web(url):
    print("Webページ解析開始:", url)
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}  # ユーザーエージェントを設定
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTPエラーがあれば例外を出す

        #  HTMLをパース（解析）
        soup = BeautifulSoup(response.text, "html.parser")

        #  記事本文を取得（多くのサイトで記事は <p> タグにある）
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)

        #  テキストがない場合の処理
        if not text.strip():
            print("⚠ 記事本文を取得できませんでした。")
            return "記事本文を取得できませんでした。"

        #  デバッグ用（最初の1000文字を出力）
        print("Web本文の一部:", text[:1000])

        return text
    except requests.exceptions.RequestException as e:
        print("Web取得エラー:", e)
        return "Webページを取得できませんでした。"

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
        if event == '要約開始':
            input_text = ""

            #  PDF処理
            if values.get('pdf_path'):
                pdf_path = values['pdf_path']
                input_text = extract_text_from_pdf(pdf_path)

            #  Web記事処理
            elif values.get('url'):
                input_text = extract_text_from_web(values['url'])

            #  テキストをGUIに表示
            window['output'].update(input_text)

            #  要約処理
            if input_text.strip():  # 空でない場合に要約する
                summary = summarize_text(input_text)
                window['summary'].update(summary)
            else:
                window['summary'].update("要約できる内容がありません。")

        if event == '取得':
            url = values.get('url', '').strip()
            if url:
                text = extract_text_from_web(url)
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
