import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final user = authProvider.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('プロフィール'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Profile header
          Center(
            child: Column(
              children: [
                Stack(
                  children: [
                    CircleAvatar(
                      radius: 50,
                      backgroundColor: Colors.blue,
                      child: const Icon(
                        Icons.person,
                        size: 50,
                        color: Colors.white,
                      ),
                    ),
                    Positioned(
                      right: 0,
                      bottom: 0,
                      child: Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.2),
                              blurRadius: 4,
                            ),
                          ],
                        ),
                        child: Icon(
                          Icons.home,
                          size: 20,
                          color: Colors.green.shade700,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  user?.email?.split('@')[0] ?? 'ユーザー',
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  user?.email ?? '',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.green.shade200),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.home,
                        size: 16,
                        color: Colors.green.shade700,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '自宅',
                        style: TextStyle(
                          color: Colors.green.shade900,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),

          // Settings sections
          const Text(
            '設定',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),

          _buildSettingsCard(
            icon: Icons.person_outline,
            title: 'プロフィール編集',
            subtitle: '名前、プロフィール写真の変更',
            onTap: () {
              // TODO: Navigate to edit profile screen
            },
          ),
          const SizedBox(height: 8),

          _buildSettingsCard(
            icon: Icons.home_outlined,
            title: '自宅住所',
            subtitle: '登録住所の変更（90日制限あり）',
            onTap: () {
              // TODO: Navigate to home address screen
            },
          ),
          const SizedBox(height: 8),

          _buildSettingsCard(
            icon: Icons.work_outline,
            title: '職場住所',
            subtitle: '登録住所の変更（90日制限あり）',
            onTap: () {
              // TODO: Navigate to work address screen
            },
          ),
          const SizedBox(height: 8),

          _buildSettingsCard(
            icon: Icons.location_on_outlined,
            title: 'カスタム場所',
            subtitle: 'ジム、カフェなどの登録',
            onTap: () {
              // TODO: Navigate to custom locations screen
            },
          ),
          const SizedBox(height: 32),

          const Text(
            'その他',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),

          _buildSettingsCard(
            icon: Icons.notifications_outlined,
            title: '通知設定',
            subtitle: 'プッシュ通知の管理',
            onTap: () {
              // TODO: Navigate to notification settings
            },
          ),
          const SizedBox(height: 8),

          _buildSettingsCard(
            icon: Icons.privacy_tip_outlined,
            title: 'プライバシー',
            subtitle: '位置情報共有設定',
            onTap: () {
              // TODO: Navigate to privacy settings
            },
          ),
          const SizedBox(height: 8),

          _buildSettingsCard(
            icon: Icons.help_outline,
            title: 'ヘルプ・サポート',
            subtitle: '使い方、お問い合わせ',
            onTap: () {
              // TODO: Navigate to help screen
            },
          ),
          const SizedBox(height: 8),

          _buildSettingsCard(
            icon: Icons.info_outline,
            title: 'アプリについて',
            subtitle: 'バージョン情報、利用規約',
            onTap: () {
              // TODO: Navigate to about screen
            },
          ),
          const SizedBox(height: 32),

          // Logout button
          ElevatedButton(
            onPressed: () async {
              final shouldLogout = await showDialog<bool>(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('ログアウト'),
                  content: const Text('ログアウトしますか?'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(false),
                      child: const Text('キャンセル'),
                    ),
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(true),
                      style: TextButton.styleFrom(
                        foregroundColor: Colors.red,
                      ),
                      child: const Text('ログアウト'),
                    ),
                  ],
                ),
              );

              if (shouldLogout == true && context.mounted) {
                await authProvider.signOut();
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red.shade50,
              foregroundColor: Colors.red.shade700,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.logout),
                SizedBox(width: 8),
                Text(
                  'ログアウト',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildSettingsCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            icon,
            color: Colors.blue,
          ),
        ),
        title: Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 16,
          ),
        ),
        subtitle: Text(
          subtitle,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
