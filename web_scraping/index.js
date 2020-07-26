import express from "express";
import playwright from "playwright";
import dateFns from "date-fns";
import lodash from "lodash";
import json2csv from "json-2-csv";

const SERVER_PORT = process.env.SERVER_PORT || 2000;

// TO-DO: replace this with Playwright's own functionality where it autowaits for elements
function waitForPageToLoad() {
  return new Promise((res, rej) =>
    setTimeout(() => {
      res();
    }, 5000)
  );
}

const server = express();
server.get("/getSymbolOHLCTimeSeries/:symbol", async (req, res) => {
  const { firefox } = playwright;
  const { format } = dateFns;
  const { get } = lodash;
  const browser = await firefox.launch({ headless: false });
  try {
    let timeSeriesData;
    const context = await browser.newContext();
    const page = await context.newPage();
    page.on("request", async (request) => {
      if (
        (await request.url()) ===
        "https://www.avanza.se/ab/component/highstockchart/getchart/orderbook"
      ) {
        timeSeriesData = await (await request.response()).json();
      }
    });

    const { symbol } = req.params;
    await page.goto("https://www.avanza.se/start");
    await page.click("button.search");
    await page.type("input.aza-input", symbol);
    await waitForPageToLoad();
    const symbolPage = await page.$eval("a.title-link", (e) => e.href);
    await page.goto(symbolPage);
    await waitForPageToLoad();
    await page.click("text=3 år");
    await waitForPageToLoad();
    await page.selectOption("select[name=grouping]", "DAY");
    await waitForPageToLoad();
    await page.click("button.marginLeft4px.actionDropToggle.area");
    await page.click("li.ohlc");
    await waitForPageToLoad();
    await page.click("span.settingsIco.icon");
    await page.click("li[data-id=volume]");
    await waitForPageToLoad();

    const dataForCSVConversion = [];
    for (let dp of timeSeriesData.dataPoints) {
      dataForCSVConversion.push({
        timestamp: format(new Date(dp[0]), "yyyy-MM-dd"),
        open: dp[1],
        high: dp[2],
        low: dp[3],
        close: dp[4],
        // TO-DO - adjusted_close, dividend_amount & split_coefficient are currently dummy values - look into fetching actual ones
        adjusted_close: dp[4],
        volume: get(
          get(timeSeriesData, "volumePoints", []).find((vp) => vp[0] === dp[0]),
          "[1]"
        ),
        dividend_amount: 0,
        split_coefficient: 1.0,
      });
    }
    dataForCSVConversion.sort((a, b) => {
      if (new Date(a.timestamp) < new Date(b.timestamp)) {
        return 1;
      }
      return -1;
    });
    await json2csv.json2csv(dataForCSVConversion, (err, csv) => {
      if (err) console.log("something went wrong with the csv generation");
      res.send(csv);
    });
  } catch (e) {
    // TO-DO: add proper logging
    console.log(e);
    res.sendStatus(500);
  } finally {
    await browser.close();
  }
});

server.listen(SERVER_PORT, () =>
  console.log(`Server running on port ${SERVER_PORT}`)
);
