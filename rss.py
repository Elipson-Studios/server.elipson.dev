import feedgenerator
import datetime

class ServerHealthRSS:
    def __init__(self):
        self.feed = feedgenerator.Rss201rev2Feed(
            title="Server Health Monitor",
            link="http://server.elipson.dev/rss",
            description="RSS feed for monitoring server health and errors.",
            language="en"
        )

    def add_error(self, error_message):
        self.feed.add_item(
            title="Server Error",
            link="http://server.elipson.dev/errors",
            description=error_message,
            pubdate=datetime.datetime.now()
        )

    def generate_feed(self):
        return self.feed.writeString('utf-8')

# Example usage
if __name__ == "__main__":
    rss = ServerHealthRSS()

    # Simulate adding a 504 error
    rss.add_error("504 Gateway Timeout error detected in server.py")

    # Generate and print the RSS feed
    print(rss.generate_feed())