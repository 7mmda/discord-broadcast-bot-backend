from flask import Blueprint, request, jsonify
import asyncio
import threading
import discord

broadcast_bp = Blueprint('broadcast', __name__)

# This will be set by the main.py file to reference the bot instance
bot_instance = None

def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot

@broadcast_bp.route('/send', methods=['POST'])
def send_broadcast():
    """
    Endpoint to send a broadcast message to Discord members.
    Expected JSON payload:
    {
        "guild_id": 123456789,
        "target_group": "all" | "online" | "offline",
        "message": "Your message here"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    guild_id = data.get('guild_id')
    target_group = data.get('target_group')
    message = data.get('message')
    
    if not guild_id or not target_group or not message:
        return jsonify({"error": "Missing required fields: guild_id, target_group, message"}), 400
    
    if target_group not in ['all', 'online', 'offline']:
        return jsonify({"error": "Invalid target_group. Must be 'all', 'online', or 'offline'"}), 400
    
    if bot_instance is None:
        return jsonify({"error": "Bot is not running"}), 503
    
    # Run the async broadcast function in the bot's event loop
    try:
        asyncio.run_coroutine_threadsafe(
            send_broadcast_message(guild_id, target_group, message),
            bot_instance.loop
        )
        return jsonify({"success": True, "message": "Broadcast initiated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


async def send_broadcast_message(guild_id: int, target_group: str, message_content: str):
    """
    Send a broadcast message to members in a guild.
    """
    import discord
    
    guild = bot_instance.get_guild(guild_id)
    if not guild:
        print(f"Guild with ID {guild_id} not found.")
        return

    target_members = []
    if target_group == 'all':
        target_members = guild.members
    elif target_group == 'online':
        target_members = [member for member in guild.members if member.status != discord.Status.offline and not member.bot]
    elif target_group == 'offline':
        target_members = [member for member in guild.members if member.status == discord.Status.offline and not member.bot]

    success_count = 0
    failed_count = 0
    
    for member in target_members:
        try:
            await member.send(message_content)
            print(f"Sent message to {member.name}")
            success_count += 1
        except discord.errors.Forbidden:
            print(f"Could not send message to {member.name} (DMs disabled or bot blocked).")
            failed_count += 1
        except Exception as e:
            print(f"Error sending message to {member.name}: {e}")
            failed_count += 1
    
    print(f"Broadcast complete: {success_count} successful, {failed_count} failed")


@broadcast_bp.route('/guilds', methods=['GET'])
def get_guilds():
    """
    Get a list of all guilds (servers) the bot is in.
    """
    if bot_instance is None:
        return jsonify({"error": "Bot is not running"}), 503
    
    print(f"Bot is in {len(bot_instance.guilds)} guilds.")
    guilds = []
    for guild in bot_instance.guilds:
        guilds.append({
            "id": guild.id,
            "name": guild.name,
            "member_count": guild.member_count
        })
    
    print(f"Returning {len(guilds)} guilds: {guilds}")
    return jsonify({"guilds": guilds}), 200


@broadcast_bp.route('/guild/<int:guild_id>/stats', methods=['GET'])
def get_guild_stats(guild_id):
    """
    Get statistics about members in a specific guild.
    """
    if bot_instance is None:
        return jsonify({"error": "Bot is not running"}), 503
    
    guild = bot_instance.get_guild(guild_id)
    if not guild:
        return jsonify({"error": "Guild not found"}), 404
    
    online_count = sum(1 for member in guild.members if member.status != discord.Status.offline and not member.bot)
    offline_count = sum(1 for member in guild.members if member.status == discord.Status.offline and not member.bot)
    total_count = guild.member_count
    
    return jsonify({
        "guild_id": guild.id,
        "guild_name": guild.name,
        "total_members": total_count,
        "online_members": online_count,
        "offline_members": offline_count
    }), 200

