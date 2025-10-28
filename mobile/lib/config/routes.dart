import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/signup_screen.dart';
import '../screens/auth/forgot_password_screen.dart';
import '../screens/main/main_tab_screen.dart';
import '../screens/profile/profile_screen.dart';
import '../providers/auth_provider.dart';

class AppRoutes {
  static const String login = '/';
  static const String signup = '/signup';
  static const String forgotPassword = '/forgot-password';
  static const String home = '/home';
  static const String profile = '/profile';

  static GoRouter createRouter(AuthProvider authProvider) {
    return GoRouter(
      initialLocation: login,
      redirect: (context, state) {
        final isAuthenticated = authProvider.isAuthenticated;
        final isOnLoginPage = state.matchedLocation == login;
        final isOnSignupPage = state.matchedLocation == signup;
        final isOnForgotPasswordPage = state.matchedLocation == forgotPassword;

        // If user is authenticated and on login/signup/forgot-password page, redirect to home
        if (isAuthenticated && (isOnLoginPage || isOnSignupPage || isOnForgotPasswordPage)) {
          return home;
        }

        // If user is not authenticated and not on login/signup/forgot-password page, redirect to login
        if (!isAuthenticated && !isOnLoginPage && !isOnSignupPage && !isOnForgotPasswordPage) {
          return login;
        }

        // No redirect needed
        return null;
      },
      refreshListenable: authProvider,
      routes: [
        GoRoute(
          path: login,
          name: 'login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: signup,
          name: 'signup',
          builder: (context, state) => const SignupScreen(),
        ),
        GoRoute(
          path: forgotPassword,
          name: 'forgot-password',
          builder: (context, state) => const ForgotPasswordScreen(),
        ),
        GoRoute(
          path: home,
          name: 'home',
          builder: (context, state) => const MainTabScreen(),
        ),
        GoRoute(
          path: profile,
          name: 'profile',
          builder: (context, state) => const ProfileScreen(),
        ),
      ],
      errorBuilder: (context, state) => Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                size: 48,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              Text(
                'ページが見つかりません',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(
                state.error?.toString() ?? '',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
