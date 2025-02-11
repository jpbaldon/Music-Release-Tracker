# Music-Release-Tracker
 An app implemeneted with PyQt that uses the iTunes API to find recent releases from followed artists

 ![image](https://github.com/user-attachments/assets/f4f5a067-9cef-49ed-baf5-850fe57d86f6)

 ## Purpose
 It can be easy to miss when your favorite artists release music. This is a simple program that can be run in the background once a month or so to see if you missed something of-interest to you.

 ## Installation
To install the required dependencies, run:
```bash
pip install -r requirements.txt
```

 ## Usage
1. Add any music artists that have content on iTunes by entering their name in the text field on the Followed Artists Tab and then clicking the Follow button
   * name of the artist must match the spelling of that artist on iTunes
   * alternatively, you can just add a list of artist names to column A of the artists.csv file before running the app
   * an example list of artists is provided (you can remove all of these at once by clicking the upper left corner of the table and clicking the unfollow button)
3. Unfollow Artists by selecting their row in the table and clicking the Unfollow Highlighted Artists button.
4. Search for recent releases from followed artists by navigating to the Albums to Check Out Tab, selecting a timeframe, and then clicking search.

## Further Info
iTunes limits the amount of get requests per ip address to about 20 per min. Consequently, this app has been written to slow down automatically if the number of artists being queried is too high to perform the get requests all at once. For this reason, this app also takes into account the number of artists in your last search, if that search was less than a minute ago. If a slowdown is necessary, this will be indicated in the GUI's text browser.

Each artist has a limit associated with them, which determines the max number of albums the iTunes server will return for that artist (before this app filters them by release date). Apple specifies that lower limits on get requests result in better response times. Consequently, this app has been written so that when an aritst is first entered into the list of Followed Artists, their default limit is 50. Each time that artist is included in a search, that limit may be adjusted up or down depending on whether iTunes returns that number of results for that artist.

  * For example: Suppose The Beatles are followed and have an initial limit of 50. When the user searches for albums, iTunes will return a max of 50 items for the beatles, even if the Beatles have more than 50 collections on iTunes. However, if the limit *is* reached, this app will increase The Beatles' limit for the next search. Conversely, if iTunes returns far less than 50 results, this app will decrease their limit for the next search in an effort to improve response times. This limit will reset to default if the user unfollows the artist and refollows them later.

 Followed artists and albums found from the most recent search are saved to CSV files. Upon closing and reopening the app, the lists that were there upon closure will persist.

If iTunes returns no albums for a particular artist (keep in mind this would be *before* the albums are filtered by release date), the text browser will indicate this. This is likely an indication that the artist name has not been spelled exactly as it is listed in iTunes OR the artist in question is one of the few musicians who does not sell content on iTunes.

A progress bar will appear when searching and should hide again when completed.
