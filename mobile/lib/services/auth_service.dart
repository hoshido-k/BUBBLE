import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  // Get current user
  User? get currentUser => _auth.currentUser;

  // Auth state changes stream
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  // Sign up with email and password
  Future<UserCredential?> signUp({
    required String email,
    required String password,
  }) async {
    try {
      final credential = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );

      // Store user ID token for API calls
      if (credential.user != null) {
        final token = await credential.user!.getIdToken();
        if (token != null) {
          await _storage.write(key: 'auth_token', value: token);
        }
      }

      return credential;
    } on FirebaseAuthException catch (e) {
      throw _handleAuthException(e);
    }
  }

  // Sign in with email and password
  Future<UserCredential?> signIn({
    required String email,
    required String password,
  }) async {
    try {
      final credential = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );

      // Store user ID token for API calls
      if (credential.user != null) {
        final token = await credential.user!.getIdToken();
        if (token != null) {
          await _storage.write(key: 'auth_token', value: token);
        }
      }

      return credential;
    } on FirebaseAuthException catch (e) {
      throw _handleAuthException(e);
    }
  }

  // Sign out
  Future<void> signOut() async {
    await _storage.delete(key: 'auth_token');
    await _auth.signOut();
  }

  // Get stored auth token
  Future<String?> getAuthToken() async {
    return await _storage.read(key: 'auth_token');
  }

  // Refresh auth token
  Future<String?> refreshToken() async {
    try {
      final user = _auth.currentUser;
      if (user != null) {
        final token = await user.getIdToken(true);
        if (token != null) {
          await _storage.write(key: 'auth_token', value: token);
        }
        return token;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  // Send password reset email
  Future<void> sendPasswordResetEmail(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email);
    } on FirebaseAuthException catch (e) {
      throw _handleAuthException(e);
    }
  }

  // Handle Firebase Auth exceptions
  String _handleAuthException(FirebaseAuthException e) {
    switch (e.code) {
      case 'weak-password':
        return 'パスワードが弱すぎます。';
      case 'email-already-in-use':
        return 'このメールアドレスは既に使用されています。';
      case 'user-not-found':
        return 'メールアドレスまたはパスワードが違います。';
      case 'wrong-password':
        return 'メールアドレスまたはパスワードが違います。';
      case 'invalid-credential':
        return 'メールアドレスまたはパスワードが違います。';
      case 'invalid-email':
        return 'メールアドレスの形式が正しくありません。';
      case 'user-disabled':
        return 'このアカウントは無効化されています。';
      case 'too-many-requests':
        return 'リクエストが多すぎます。しばらく待ってから再試行してください。';
      case 'operation-not-allowed':
        return 'この操作は許可されていません。';
      case 'network-request-failed':
        return 'ネットワーク接続を確認してください。';
      default:
        return '認証エラーが発生しました: ${e.message}';
    }
  }
}
