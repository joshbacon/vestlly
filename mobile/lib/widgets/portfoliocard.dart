import 'package:flutter/material.dart';
import 'package:vestlly/models/account.dart';
import 'package:vestlly/models/statemanager.dart';
import 'package:vestlly/pages/portfoliopage.dart';

class PortfolioCard extends StatefulWidget {
  final Account data;

  const PortfolioCard(this.data, {Key? key}) : super(key: key);

  @override
  State<PortfolioCard> createState() => _PortfolioCardState();
}

class _PortfolioCardState extends State<PortfolioCard> {

  @override
  Widget build(BuildContext context) {

    final totalContribs = widget.data.contributions.last;
    final totalWDs = widget.data.withdrawals.last;
    var growth = (widget.data.value / (totalContribs + totalWDs)) - 1;
    if (totalWDs > totalContribs && widget.data.value == 0.0) {
      growth = growth * -1;
    }
    
    return Card(
      clipBehavior: Clip.hardEdge,
      child: InkWell(
        splashColor: Theme.of(context).colorScheme.primary,
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => PortfolioPage(widget.data)),
          );
        },
        child: ListTile(
          leading: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.data.type,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              Text(
                widget.data.institution,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey,
                ),
              ),
            ]
          ),
          trailing: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(StateManager.currencyFormater.format(widget.data.value)),
              Text(
                "${StateManager.currencyFormater.format(widget.data.value-totalContribs)} (${StateManager.percentFormater(growth)})",
                style: TextStyle(
                  color: growth >= 0 ? Colors.lightGreen : Colors.red,
                ),
              ),
            ]
          ),
        ),
      ),
    );
  }
}