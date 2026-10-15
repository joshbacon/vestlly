import 'package:flutter/material.dart';
import 'package:vestlly/models/automationparams.dart';

class AutomationCard extends StatefulWidget {
  final AutomationParameters data;

  const AutomationCard(this.data, {Key? key}) : super(key: key);

  @override
  State<AutomationCard> createState() => _AutomationCardState();
}

class _AutomationCardState extends State<AutomationCard> {

  // if in use:
  // - have a weight field
  // - have all necessary parameters (e.g. stop loss amount, either dollar or percent)
  // - percent of buying power to use

  static const WidgetStateProperty<Icon> thumbIcon =
    WidgetStateProperty<Icon>.fromMap(<WidgetStatesConstraint, Icon>{
      WidgetState.selected: Icon(Icons.check),
      WidgetState.any: Icon(Icons.close),
    });

  String selected = "Linear";

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(height: 10.0),
        Row(
          children: [
            Text(widget.data.title),
            SizedBox(width: 10.0),
            Switch(
              value: widget.data.toggled,
              thumbIcon: thumbIcon,
              activeThumbColor: Theme.of(context).colorScheme.primary,
              onChanged: (bool value) {
                setState(() {
                  widget.data.toggled = value;
                });
              },
            ),
            Spacer(),
            Visibility(
              visible: widget.data.toggled,
              child: Row(
                children: [
                  Text("Target"),
                  SizedBox(width: 8.0),
                  SizedBox(
                    width: 60,
                    child: TextField(
                      textAlign: TextAlign.center,
                      decoration: InputDecoration(
                        hintText: widget.data.target.toString(),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ]
        ),
        Visibility(
          visible: widget.data.toggled,
          child: Row(
            children: [
              Spacer(),
              Text("Weight"),
              SizedBox(width: 8.0),
              SizedBox(
                width: 60,
                child: TextField(
                  textAlign: TextAlign.center,
                  decoration: InputDecoration(
                    hintText: widget.data.weight.toString(),
                  ),
                ),
              ),
            ]
          ),
        ),
        Visibility(
          visible: widget.data.toggled,
          child: SegmentedButton(
            selected: <String>{selected},
            onSelectionChanged: (Set<String> newSelection) {
              setState(() {
                selected = newSelection.first;
              });
            },
            multiSelectionEnabled: false,
            segments: const <ButtonSegment<String>>[
              ButtonSegment(
                value: "Linear",
                label: Text("Linear"),
              ),
              ButtonSegment(
                value: "Squared",
                label: Text("Squared"),
              ),
            ],
          ),
        ),
        Divider(),
      ]
    );
  }
}