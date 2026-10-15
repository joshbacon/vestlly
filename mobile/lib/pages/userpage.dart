import 'package:flutter/material.dart';

class UserPage extends StatefulWidget {
  const UserPage({super.key});

  @override
  State<UserPage> createState() => _UserPageState();
}

class _UserPageState extends State<UserPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Have user data:
      // - date joined
      // - connected brokerages
      // - # automated trades
      body: Padding(
        padding: EdgeInsets.fromLTRB(15.0, 35.0, 15.0, 50.0),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(8.0),
          child: Image(
            image: AssetImage("assets/icon.png"),
          ),
        ),
      ),
    );
  }
}