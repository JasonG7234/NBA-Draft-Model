# NBA Draft Model

This is a Python college basketball data scraper + draft model.

## Installation

Install the relevant requirements with:

```bash
pip3 install -r requirements.txt
```

## Usage

As of 4/27/20, we only have support for a basic data scraper (pulling all college basketball prospects since 2009) and a very basic graphing utility with the stats pulled from scraping.  

### Data Scraper

To use the data scraper, just call `python getCollegeStats.py` and it will generate a CSV of 1000+ prospects. I suggest pausing after Step 2 to do some manual data cleanup, because some players are left with funky names and w/o obvious RSCI ranks. I'm working on fixing that, but not in the plans right now. 

### Graph

Once you have the master.csv file populated, you can plot some simple scatter plots by calling `py graph.py` and following the steps. It's a super simple way to draw some baseline conclusions about successful college basketball prospects. Below is a graph I made comparing RSCI ranks with college win shares. 

![Image of Graph](https://i.imgur.com/KO5MKXJ.png)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

If you have any questions, you can reach out to me on twitter [@MilosTeodopesic](https://twitter.com/MilosTeodopesic) or shoot me an email at [JasonG7234@gmail.com](mailto:JasonG7234@gmail.com).

## License
[MIT](LICENSE)