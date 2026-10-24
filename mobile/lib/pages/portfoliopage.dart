import "dart:math";
import 'package:flutter/material.dart';
import 'package:vestlly/models/db.dart';
import 'package:vestlly/models/account.dart';
import 'package:vestlly/models/holding.dart';
import 'package:vestlly/models/order.dart';
import 'package:vestlly/models/trade.dart';
import 'package:vestlly/models/stock.dart';
import 'package:vestlly/widgets/scheduler.dart';
import 'package:vestlly/widgets/stockcard.dart';
import 'package:vestlly/widgets/holdingcard.dart';
import 'package:vestlly/widgets/ordercard.dart';
import 'package:vestlly/widgets/tradecard.dart';
import 'package:vestlly/widgets/transfercard.dart';
import 'package:vestlly/models/statemanager.dart';
import 'package:vestlly/pages/stockpage.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:provider/provider.dart';
import 'package:animated_bottom_navigation_bar/animated_bottom_navigation_bar.dart';
import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';


class PortfolioPage extends StatefulWidget {
  final Account data;

  const PortfolioPage(this.data, {Key? key}) : super(key: key);

  @override
  State<PortfolioPage> createState() => _PortfolioPageState();
}

class _PortfolioPageState extends State<PortfolioPage> {

  final DB database = DB();

  int _bottomNavIndex = 0;
  bool sortToggle = false;

  // create a model for a schedule,
  // - include a toggle variable

  @override
  Widget build(BuildContext context) {
    
    final totalContribs = widget.data.contributions.last;
    final totalWDs = widget.data.withdrawals.last;
    var growth = (widget.data.value / (totalContribs + totalWDs)) - 1;

    if (totalWDs > totalContribs && widget.data.value == 0.0) {
      growth = growth * -1;
    }

    List<FlSpot> values = widget.data.performance.asMap().entries
      .map((e) => FlSpot(e.key.toDouble(), e.value)).toList();

    List<FlSpot> contribs = widget.data.contributions.asMap().entries
      .map((e) => FlSpot(e.key.toDouble(), e.value)).toList();

    final List<Widget> _pages = [
      Padding( // Account Home
        padding: EdgeInsets.fromLTRB(15.0, 35.0, 15.0, 50.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ElevatedButton(
              onPressed: Navigator.of(context).pop,
              child: const Icon(Icons.arrow_back),
            ),
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                StateManager.currencyFormater.format(widget.data.value),
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                widget.data.name,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Theme.of(context).colorScheme.primary
                ),
              ),
            ),
            Align(
              alignment: Alignment.centerRight,
              child: Text(widget.data.institution),
            ),
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                "${StateManager.currencyFormater.format(widget.data.value-totalContribs)} (${StateManager.percentFormater(growth)})",
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: growth >= 0 ? Colors.lightGreen : Colors.red,
                ),
              ),
            ),
            Align(
              alignment: Alignment.centerRight,
              child: Text("${StateManager.currencyFormater.format(totalContribs)} contributed"),
            ),
            SizedBox(height: 10.0),
            SizedBox(
              height: 85.0,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8.0),
                child: LineChart(
                  LineChartData(
                    minY: [widget.data.performance, widget.data.contributions].expand((list) => list).reduce(min) * 0.8,
                    maxY: [widget.data.performance, widget.data.contributions].expand((list) => list).reduce(max) * 1.2,
                    gridData: FlGridData(
                      show: true,
                      getDrawingHorizontalLine: (_) =>
                        FlLine(color: Colors.white10, strokeWidth: 1),
                      getDrawingVerticalLine: (_) =>
                        FlLine(color: Colors.white10, strokeWidth: 1),
                    ),
                    borderData: FlBorderData(show: false),
                    titlesData: FlTitlesData(
                      leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                      topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                      rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                      bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    ),
                    lineTouchData: LineTouchData(
                      touchTooltipData: LineTouchTooltipData(
                        getTooltipItems: (spots) => spots
                          .map((s) => null).toList()
                      ),
                    ),
                    lineBarsData: [
                      LineChartBarData(
                        spots: contribs,
                        isCurved: true,
                        color: Colors.grey,
                        barWidth: 2.5,
                        dotData: FlDotData(show: false),
                      ),
                      LineChartBarData(
                        spots: values,
                        isCurved: true,
                        color: growth >= 0 ? Colors.greenAccent : Colors.redAccent,
                        barWidth: 2.5,
                        dotData: FlDotData(show: false),
                        belowBarData: BarAreaData(
                          show: true,
                          color: (growth >= 0 ? Colors.greenAccent : Colors.redAccent).withOpacity(0.1),
                        ),
                      )
                    ]
                  ),
                ),
              ),
            ),
            SizedBox(height: 15.0),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Spacer(),
                        Text(StateManager.currencyFormater.format(7)),
                        Text(
                          "   Cash",
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                      ]
                    ),
                    Text(
                      "   Holdings",
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                    FutureBuilder<List<Map<String, dynamic>>>(
                      future: database.getHoldings(widget.data.account_id),
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.waiting) {
                          return const Center(child: CircularProgressIndicator());
                        }
                        if (snapshot.hasError) {
                          return Padding(
                            padding: EdgeInsets.only(top: 30.0, bottom: 10.0),
                            child: Align(
                              alignment: Alignment.center,
                              child: Text(
                                'Error: ${snapshot.error}',
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Theme.of(context).colorScheme.onBackground?.withOpacity(0.5),
                                ),
                              ),
                            ),
                          );
                        }
                        final holdings = snapshot.data ?? [];
                        if (holdings.isEmpty) {
                          return Padding(
                            padding: EdgeInsets.only(top: 30.0, bottom: 10.0),
                            child: Align(
                              alignment: Alignment.center,
                              child: Text(
                                'No current holdings',
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Theme.of(context).colorScheme.onBackground?.withOpacity(0.5),
                                ),
                              ),
                            ),
                          );
                        }
                        return Column(
                          children: holdings.map((holding) {
                            return HoldingCard(Holding.fromMap(holding));
                          }).toList(),
                        );
                      },
                    ),
                  ]
                )
              ),
            ),
            SizedBox(height: 75),
          ]
        ),
      ),
      Padding( // Account Log
        padding: EdgeInsets.fromLTRB(15.0, 35.0, 15.0, 50.0),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: Navigator.of(context).pop,
                  child: const Icon(Icons.arrow_back),
                ),
                Text(
                  "History",
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ),
              ]
            ),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.start,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(height: 20.0),
                    FutureBuilder<List<Map<String, dynamic>>>(
                      future: Provider.of<StateManager>(context, listen: false).getTradePairs(widget.data.account_id),
                      // future: database.getTrades(widget.data.account_id),
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.waiting) {
                          return const Center(child: CircularProgressIndicator());
                        }
                        if (snapshot.hasError) {
                          return Padding(
                            padding: EdgeInsets.only(top: 30.0, bottom: 10.0),
                            child: Align(
                              alignment: Alignment.center,
                              child: Text(
                                'Error: ${snapshot.error}',
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Theme.of(context).colorScheme.onBackground?.withOpacity(0.5),
                                ),
                              ),
                            ),
                          );
                        }
                        final trades = snapshot.data ?? [];
                        if (trades.isEmpty) {
                          return Padding(
                            padding: EdgeInsets.only(top: 30.0, bottom: 10.0),
                            child: Align(
                              alignment: Alignment.center,
                              child: Text(
                                'No trades found',
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Theme.of(context).colorScheme.onBackground?.withOpacity(0.5),
                                ),
                              ),
                            ),
                          );
                        }
                        return Column(
                          children: trades.map((trade) {
                            if (trade["type"] == 'TRANSFER')
                              return(TransferCard(trade['trade']));
                            else return TradeCard(trade['trade']);
                          }).toList(),
                        );
                      },
                    ),
                    SizedBox(height: 75),
                  ]
                ),
              ),
            ),
          ]
        ),
      ),
      Padding( // Account Assets
        padding: EdgeInsets.fromLTRB(15.0, 35.0, 15.0, 50.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: Navigator.of(context).pop,
                  child: const Icon(Icons.arrow_back),
                ),
                IconButton(
                  icon: Icon(
                    sortToggle ? Icons.keyboard_arrow_down: Icons.keyboard_arrow_up,
                    color: Theme.of(context).colorScheme.primary,
                    size: 32.0,
                  ),
                  onPressed: () {
                    setState(() {
                      sortToggle = !sortToggle;
                    });
                  }
                ),
              ]
            ),
            FutureBuilder<List<Map<String, dynamic>>>(
              future: database.getStocks(sortToggle ? "score ASC" : "score DESC", widget.data.account_id),
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  return Center(child: Text('Error: ${snapshot.error}'));
                }
                final stocks = snapshot.data ?? [];
                if (stocks.isEmpty) {
                  return const Center(child: Text('No stock data found.'));
                }
                return Expanded(
                  child: MasonryGridView.count(
                    crossAxisCount: 2,
                    mainAxisSpacing: 4,
                    crossAxisSpacing: 4,
                    itemCount: stocks.length,
                    itemBuilder: (context, index) {
                      return StockCard(Stock.fromMap(stocks[index]));
                    }
                  )
                );
              },
            ),
          ]
        )
      ),
      Padding( // Account Automations
        padding: EdgeInsets.fromLTRB(15.0, 35.0, 15.0, 50.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ElevatedButton(
              onPressed: Navigator.of(context).pop,
              child: const Icon(Icons.arrow_back),
            ),
            SizedBox(height: 5.0),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.start,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  spacing: 10.0,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Text("Automated trades are currently"),
                        Text("ON", style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Theme.of(context).colorScheme.primary,
                        ),),
                      ],
                    ),
                    ElevatedButton(
                      onPressed: () {
                        // TODO: wire up the toggle with the schedule model
                        showDialog<void>(
                          context: context,
                          barrierDismissible: false, // user must tap button!
                          builder: (BuildContext context) {
                            return AlertDialog(
                              title: const Text('Toggle Trading'),
                              content: const SingleChildScrollView(
                                child: ListBody(
                                  children: <Widget>[
                                    Text('Are you sure?'),
                                  ],
                                ),
                              ),
                              actions: <Widget>[
                                TextButton(
                                  onPressed: () => Navigator.pop(context, false),
                                  child: Text('Nevermind', style: TextStyle(color: Theme.of(context).colorScheme.primary.withAlpha(120))),
                                ),
                                TextButton(
                                  onPressed: () => Navigator.pop(context, true),
                                  child: const Text('Start', style: TextStyle(color:Colors.lightGreen)),
                                  // child: const Text('Halt', style: TextStyle(color:Colors.red)),
                                ),
                              ],
                            );
                          },
                        );
                      },
                      style: ButtonStyle(
                        fixedSize: WidgetStateProperty.all(Size(256, 64)),
                        // iconColor: WidgetStateProperty.all(Colors.lightGreen),
                        // backgroundColor: WidgetStateProperty.all(Colors.lightGreenAccent),
                        iconColor: WidgetStateProperty.all(Colors.red),
                        backgroundColor: WidgetStateProperty.all(const Color.fromARGB(61, 255, 82, 82)),
                      ),
                      child: Icon(
                        // Icons.play_arrow_rounded,
                        Icons.back_hand,
                        // size: 48,
                        size: 28,
                      ),
                    ),
                    Divider(),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(
                          "Scheduling",
                          style: Theme.of(context).textTheme.titleMedium,
                        )
                      ]
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text("Mon, Thu, Fri at 11:00 AM"),
                      ]
                    ),
                    Scheduler(value: {"startTime": "9:15AM"}, selected: () {},),
                    Divider(),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(
                          "Stock Pool",
                          style: Theme.of(context).textTheme.titleMedium,
                        )
                      ]
                    ),
                    // TODO: have a checklist of the stocks that are considered on each run
                    FutureBuilder<List<Map<String, dynamic>>>(
                      future: database.getStocks(sortToggle ? "score ASC" : "score DESC", widget.data.account_id),
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.waiting) {
                          return const Center(child: CircularProgressIndicator());
                        }
                        if (snapshot.hasError) {
                          return Center(child: Text('Error: ${snapshot.error}'));
                        }
                        final stocks = snapshot.data ?? [];
                        if (stocks.isEmpty) {
                          return const Center(child: Text('No stock data found.'));
                        }
                        return Column(
                          children: [
                            // TODO: group these by sector
                            // - put in grid view, one card per sector
                            for (final stock in stocks)  
                              Row(
                                children: [
                                  Checkbox(value: false, onChanged: (_) {}),
                                  Text(stock['ticker']),
                                ],
                              ),
                          ],
                        );
                        // return Expanded(
                        //   child: MasonryGridView.count(
                        //     crossAxisCount: 2,
                        //     mainAxisSpacing: 4,
                        //     crossAxisSpacing: 4,
                        //     itemCount: stocks.length,
                        //     itemBuilder: (context, index) {
                        //       return StockCard(Stock.fromMap(stocks[index]));
                        //     }
                        //   )
                        // );
                      },
                    ),
                  ]
                )
              )
            )
          ],
        ),
      ),
    ];
    
    return Scaffold(
      extendBody: true,
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: AnimatedBottomNavigationBar(
        icons: [Icons.home, Icons.receipt, Icons.candlestick_chart_sharp, Icons.settings_suggest],
        activeIndex: _bottomNavIndex,
        gapLocation: GapLocation.none,
        notchSmoothness: NotchSmoothness.verySmoothEdge,
        activeColor: Theme.of(context).colorScheme.primary,
        backgroundColor: Theme.of(context).colorScheme.surface,
        leftCornerRadius: 8,
        rightCornerRadius: 8,
        onTap: (index) => setState(() => _bottomNavIndex = index),
      ),
      body: _pages[_bottomNavIndex],
    );
  }
}