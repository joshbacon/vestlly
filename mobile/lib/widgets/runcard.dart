import 'package:flutter/material.dart';
import 'package:vestlly/models/statemanager.dart';

class RunCard extends StatelessWidget {
  
  final double tempConfidence;
  const RunCard(this.tempConfidence, {Key? key}) : super(key: key);

  // TODO: try to have it open a drawer from the right to show the decision making process pargraph on tap
  // - also include the weight breakdown across active indicators

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(8.0),
        child:Column(
          children: [
            Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8.0),
                  child: Container(
                    width: 64.0,
                    height: 64.0,
                    color: Theme.of(context).colorScheme.surfaceContainerHighest,
                    child: Center(
                      child:Text(
                        "${(tempConfidence*100).round()}%",
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Color.fromRGBO((255*(1-tempConfidence)).round(), (255*(tempConfidence)).round(), 125, 1),
                        ),
                      ),
                    ),
                  ),
                ),
                SizedBox(width: 10.0),
                Column(
                  mainAxisAlignment: MainAxisAlignment.start,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Buy Order", // "Sell Order", "Hold"
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    Text(
                      "2026-3-9 23:46",
                      style: Theme.of(context).textTheme.titleSmall,
                    ),
                  ]
                )
              ]
            ),
            // Text("Thought process description"),
            // Text("Resulting order placed (or N/A) - FILLED"),
            // Text("Resulting order placed (or N/A) - EXPIRED"),
            // Text("Resulting order placed (or N/A) - OPEN"),
            SizedBox(height: 10.0),
            Row(
              children: [
                Text(
                  "4 x WCP.TO @ \$12.51",
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                Spacer(),
                Text(
                  "FILLED", // "EXPIRED", "OPEN"
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: "VARIABLE HERE" == "FILLED" ? Colors.lightGreen : "VARIABLE HERE" == "EXPIRED" ? Colors.pink : Theme.of(context).colorScheme.primary,
                  ),
                ),
              ]
            ),
          ]
        ),
      ),
    );
  }
}