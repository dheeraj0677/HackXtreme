import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:global_sentry_app/main.dart';

void main() {
  testWidgets('GlobalSentry app smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const GlobalSentryApp());
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
