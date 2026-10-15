import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:vestlly/models/account.dart';
import 'package:vestlly/widgets/runcard.dart';
import 'package:vestlly/models/trade.dart';
import 'package:vestlly/models/statemanager.dart';
import 'package:vestlly/widgets/automationcard.dart';
import 'package:vestlly/models/automationparams.dart';

class AutomationPage extends StatefulWidget {
  final Account data;

  const AutomationPage(this.data, {Key? key}) : super(key: key);

  @override
  State<AutomationPage> createState() => _AutomationPageState();
}

class _AutomationPageState extends State<AutomationPage> {

  @override
  Widget build(BuildContext context) {
    final state = context.watch<StateManager>();
    
    bool epsOn = true;
    bool peOn = true;

    const WidgetStateProperty<Icon> thumbIcon =
      WidgetStateProperty<Icon>.fromMap(<WidgetStatesConstraint, Icon>{
        WidgetState.selected: Icon(Icons.check),
        WidgetState.any: Icon(Icons.close),
      });

    return Scaffold(
      body: Padding(
        padding: EdgeInsets.fromLTRB(15.0, 35.0, 15.0, 50.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ElevatedButton(
              onPressed: Navigator.of(context).pop,
              child: const Icon(Icons.arrow_back),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.fromLTRB(5.0, 10.0, 8.0, 5.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Parameters",
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                    AutomationCard(AutomationParameters(
                      title: "PEG",
                      target: 1,
                      weight: 1,
                      toggled: false
                    )),
                    AutomationCard(AutomationParameters(
                      title: "EPS",
                      target: 3.5,
                      weight: 1,
                      toggled: false
                    )),
                    AutomationCard(AutomationParameters(
                      title: "P/E",
                      target: 12.6,
                      weight: 1,
                      toggled: false
                    )),
                    AutomationCard(AutomationParameters(
                      title: "P/B",
                      target: 1.5,
                      weight: 1,
                      toggled: false
                    )),
                    SizedBox(height: 10.0),
                    Align(
                      alignment: Alignment.center,
                      child: FloatingActionButton.extended(
                        label: Text("Save"),
                        icon: Icon(Icons.backup),
                        onPressed: () {}
                      ),
                    ),
                    SizedBox(height: 10.0),
                    Text(
                      "History",
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ]
        ),
      ),
    );
  }
}