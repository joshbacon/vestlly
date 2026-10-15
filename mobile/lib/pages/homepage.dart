import 'dart:math';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:vestlly/models/db.dart';
import 'package:vestlly/models/statemanager.dart';
import 'package:vestlly/models/account.dart';
import 'package:vestlly/widgets/portfoliocard.dart';
import 'package:animated_snack_bar/animated_snack_bar.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {

  bool isLoading = false;
  final DB database = DB();

  @override
  Widget build(BuildContext context) {
    final state = context.watch<StateManager>();
    var growth = (state.totalValue / state.totalContrib) - 1;
    if (state.totalWithdrawal*-1 > state.totalContrib && state.totalValue == 0.0) {
      growth = growth * -1;
    }

    return Scaffold(
      body: RefreshIndicator(
        color: Theme.of(context).colorScheme.onSecondary,
        backgroundColor: Theme.of(context).colorScheme.secondary,
        onRefresh: () async {
          setState(() {
            isLoading = true;
          });
          Provider.of<StateManager>(context, listen: false).fetchSTData().then((result) {
            if (result == 200) {
              AnimatedSnackBar.material(
                'Reload successful',
                type: AnimatedSnackBarType.success,
                duration: const Duration(seconds: 3),
              ).show(context);
            } else {
              AnimatedSnackBar.material(
                'Reload failed (${result})',
                type: AnimatedSnackBarType.error,
                duration: const Duration(seconds: 5),
              ).show(context);
            }
            setState(() {
              isLoading = false;
            });
          });
        },
        child: Stack(
          children: [
            if (isLoading) Positioned(
              top: 50.0,
              left: (MediaQuery.of(context).size.width / 2) - (50.0 / 2),
              child: SpinKitRipple(
                color: Theme.of(context).colorScheme.primary,
                size: 50.0,
              ),
            ),
            Padding(
              padding: EdgeInsets.fromLTRB(15.0, 35.0, 15.0, 50.0),
              child: Center(
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  child: Column(
                    mainAxisSize: MainAxisSize.max,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      SizedBox(height: 10.0),
                      Text(
                        "Last Updated: ${state.lastUpdated.year}-${state.lastUpdated.month}-${state.lastUpdated.day} ${state.lastUpdated.hour}:${state.lastUpdated.minute < 10 ? '0' : ''}${state.lastUpdated.minute}",
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.onBackground?.withOpacity(0.5),
                        ),
                      ),
                      SizedBox(height: 20.0),
                      Text(
                        "Total Portfolio Value",
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Theme.of(context).colorScheme.primary,
                        ),
                      ),
                      SizedBox(height: 8.0),
                      Text(
                        StateManager.currencyFormater.format(state.totalValue),
                        style: Theme.of(context).textTheme.titleLarge
                      ),
                      SizedBox(height: 8.0),
                      Text(
                        "${StateManager.currencyFormater.format(state.totalValue-state.totalContrib)} (${StateManager.percentFormater(growth)})",
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: growth >= 0 ? Colors.lightGreen : Colors.red,
                        ),
                      ),
                      SizedBox(height: 25.0),
                      Row(
                        children: [
                          Text(
                            "   Accounts",
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: Theme.of(context).colorScheme.primary,
                            ),
                          ),
                        ]
                      ),
                      SizedBox(height: 5.0),
                      FutureBuilder<List<Map<String, dynamic>>>(
                        future: database.getAccounts(),
                        builder: (context, snapshot) {
                          if (snapshot.connectionState == ConnectionState.waiting) {
                            return const Center(child: CircularProgressIndicator());
                          }
                          if (snapshot.hasError) {
                            return Center(child: Text('Error: ${snapshot.error}'));
                          }
                          final accounts = snapshot.data ?? [];
                          if (accounts.isEmpty) {
                            return const Center(child: Text('No accounts found.'));
                          }
                          return Column(
                            children: accounts.map((account) {
                              return PortfolioCard(Account.fromMap(account));
                            }).toList(),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ]
        ),
      ),
    );
  }
}