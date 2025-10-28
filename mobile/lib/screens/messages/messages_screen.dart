import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class MessagesScreen extends StatelessWidget {
  const MessagesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('メッセージ'),
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
          _buildMessageCard(
            name: '田中太郎',
            lastMessage: '了解しました！',
            timestamp: '2分前',
            unreadCount: 2,
            avatar: Icons.person,
          ),
          const SizedBox(height: 8),
          _buildMessageCard(
            name: '佐藤花子',
            lastMessage: 'ありがとうございます',
            timestamp: '1時間前',
            unreadCount: 0,
            avatar: Icons.person,
          ),
          const SizedBox(height: 8),
          _buildMessageCard(
            name: '鈴木一郎',
            lastMessage: '今日は忙しいです',
            timestamp: '昨日',
            unreadCount: 0,
            avatar: Icons.person,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        heroTag: 'messages_fab',
        onPressed: () {
          // TODO: Navigate to new message screen
        },
        child: const Icon(Icons.edit),
      ),
    );
  }

  Widget _buildMessageCard({
    required String name,
    required String lastMessage,
    required String timestamp,
    required int unreadCount,
    required IconData avatar,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.blue,
          child: Icon(avatar, color: Colors.white),
        ),
        title: Row(
          children: [
            Expanded(
              child: Text(
                name,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ),
            Text(
              timestamp,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
        subtitle: Row(
          children: [
            Expanded(
              child: Text(
                lastMessage,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: unreadCount > 0 ? Colors.black87 : Colors.grey[600],
                  fontWeight:
                      unreadCount > 0 ? FontWeight.w500 : FontWeight.normal,
                ),
              ),
            ),
            if (unreadCount > 0)
              Container(
                margin: const EdgeInsets.only(left: 8),
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 2,
                ),
                decoration: BoxDecoration(
                  color: Colors.red,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  unreadCount.toString(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
          ],
        ),
        onTap: () {
          // TODO: Navigate to chat screen
        },
      ),
    );
  }
}
