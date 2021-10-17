from wox import Wox

from find_text import FindText


class FindTextWox(Wox):
    def query(self, query: str):
        if len(query) == 0:
            return [{
                "Title": "Type in text to search the currently visible screen.",
                "IcoPath": "Images\\findtext.png",
                "Subtitle": "You may have to wait a moment for the scan to complete after typing.",
            }]

        return [{
            "Title": f"Press enter to search the screen for \"{query}\"",
            "IcoPath": "Images\\findtext.png",
            "Subtitle": "You may have to wait a moment for the scan to complete after searching.",
            "JsonRPCAction": {
                "method": "search_screen",
                "parameters": [
                    query
                ]
            }
        }]

    def search_screen(self, query: str):
        if len(query) == 0:
            return
        finder = FindText()
        finder.search(query)
        finder.root.mainloop()


if __name__ == '__main__':
    FindTextWox()
