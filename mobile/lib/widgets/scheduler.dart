import 'package:flutter/material.dart';

class Scheduler extends StatelessWidget {

  const Scheduler({
    super.key,
    required this.value,
    required this.selected,
  });

  final value;
  final selected;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 12.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Repeat on',
              style: Theme.of(context).textTheme.titleMedium
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                for (final day in ['M', 'T', 'W', 'Th', 'F', 'Sat', 'Sun'])
                  InkWell(
                    splashColor: Theme.of(context).colorScheme.primary,
                    // TODO: set the style of the days dynamically based on if they're selected
                    child: Text(day, style: TextStyle(fontWeight: FontWeight.bold, color: Theme.of(context).colorScheme.primary),)
                  ),
              ],
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Every day'),
              value: true,
              onChanged: (on) => selected(
                value.copyWith(
                  days: on ? 'all' : 'm',
                ),
              ),
            ),
            Divider(),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.schedule),
              title: Text('Run time', style: Theme.of(context).textTheme.titleMedium,),
              trailing: Text(
                "11:00 AM", // TODO: make this dynamic
                style: Theme.of(context).textTheme.titleMedium,
              ),
              // TODO: make the onTap bring up a date picker and update accordingly
              // onTap: () => _pickTime(context),
            ),
          ],
        ),
      ),
    );
  }
}