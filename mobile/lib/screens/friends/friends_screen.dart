import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class FriendsScreen extends StatelessWidget {
  const FriendsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('フレンド'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: IconButton(
              onPressed: () {
                context.push('/profile');
              },
              icon: Stack(
                children: [
                  CircleAvatar(
                    radius: 18,
                    backgroundColor: Colors.white,
                    child: const Icon(
                      Icons.person,
                      size: 20,
                      color: Colors.blue,
                    ),
                  ),
                  Positioned(
                    right: 0,
                    bottom: 0,
                    child: Container(
                      padding: const EdgeInsets.all(3),
                      decoration: BoxDecoration(
                        color: Colors.blue,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: Colors.white,
                          width: 1.5,
                        ),
                      ),
                      child: Icon(
                        Icons.home,
                        size: 10,
                        color: Colors.green.shade400,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          _buildFriendCard(
            name: '田中太郎',
            status: 'home',
            statusText: '自宅',
            statusColor: Colors.green,
            avatar: Icons.person,
          ),
          const SizedBox(height: 8),
          _buildFriendCard(
            name: '佐藤花子',
            status: 'work',
            statusText: '職場',
            statusColor: Colors.blue,
            avatar: Icons.person,
          ),
          const SizedBox(height: 8),
          _buildFriendCard(
            name: '鈴木一郎',
            status: 'moving',
            statusText: '移動中',
            statusColor: Colors.orange,
            avatar: Icons.person,
          ),
          const SizedBox(height: 8),
          _buildFriendCard(
            name: '高橋美咲',
            status: 'unknown',
            statusText: '不明',
            statusColor: Colors.grey,
            avatar: Icons.person,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        heroTag: 'friends_fab',
        onPressed: () {
          // TODO: Navigate to add friend screen
        },
        child: const Icon(Icons.person_add),
      ),
    );
  }

  Widget _buildFriendCard({
    required String name,
    required String status,
    required String statusText,
    required Color statusColor,
    required IconData avatar,
  }) {
    IconData statusIcon;
    switch (status) {
      case 'home':
        statusIcon = Icons.home;
        break;
      case 'work':
        statusIcon = Icons.work;
        break;
      case 'moving':
        statusIcon = Icons.directions_walk;
        break;
      default:
        statusIcon = Icons.help_outline;
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        leading: Stack(
          children: [
            CircleAvatar(
              backgroundColor: Colors.blue,
              child: Icon(avatar, color: Colors.white),
            ),
            Positioned(
              right: 0,
              bottom: 0,
              child: Container(
                padding: const EdgeInsets.all(2),
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  statusIcon,
                  size: 16,
                  color: statusColor,
                ),
              ),
            ),
          ],
        ),
        title: Text(
          name,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        subtitle: Row(
          children: [
            Icon(
              statusIcon,
              size: 14,
              color: statusColor,
            ),
            const SizedBox(width: 4),
            Text(
              statusText,
              style: TextStyle(
                color: statusColor,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.more_vert),
          onPressed: () {
            // TODO: Show friend options
          },
        ),
        onTap: () {
          // TODO: Navigate to friend detail screen
        },
      ),
    );
  }
}
