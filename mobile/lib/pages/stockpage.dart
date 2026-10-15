import 'package:flutter/material.dart';
import 'package:vestlly/models/db.dart';
import 'package:vestlly/models/account.dart';
import 'package:vestlly/models/stock.dart';
import 'package:vestlly/widgets/stockcard.dart';
import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';

class StockPage extends StatefulWidget {
  final Account data;

  const StockPage(this.data, {Key? key}) : super(key: key);

  @override
  State<StockPage> createState() => _StockPageState();
}

class _StockPageState extends State<StockPage> {

  final DB database = DB();
  bool sortToggle = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      body: Padding(
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
                  icon: Icon(sortToggle ? Icons.keyboard_arrow_down: Icons.keyboard_arrow_up),
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
      )
    );
  }
}