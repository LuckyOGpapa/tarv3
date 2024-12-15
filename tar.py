import asyncio
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipant

# Bot Configuration
API_ID = '24509589'
API_HASH = '717cf21d94c4934bcbe1eaa1ad86ae75'
BOT_TOKEN = '7505586183:AAH0LWzUWb8LV_2T2SToz36lGEjJ1pNfmKI'
CHANNEL_USERNAME = 'Pvtshits'  # Replace with your channel username
ADMIN_USERNAME = 'Kiltes'  # Replace with admin username

bot = TelegramClient('new_report_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Global Variables
user_reporting = {}  # To track reporting state
notified_users = set()  # To track already notified users
active_users = set()  # To store all bot users for broadcast
broadcasting = False  # Flag to prevent multiple broadcasts at the same time
waiting_for_broadcast_message = None  # To store the admin who is sending the broadcast message
broadcast_message_content = None  # Store the broadcast message content
ADMIN_ID = 6652287427  # Replace with the admin's Telegram ID

# Helper Function: Check Channel Membership
async def is_user_in_channel(user_id):
    try:
        participant = await bot(GetParticipantRequest(CHANNEL_USERNAME, user_id))
        return isinstance(participant.participant, ChannelParticipant)
    except:
        return False

# Start Command: Force Join + Notify Admin
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    user = await bot.get_entity(user_id)
    username = user.username or "No Username"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    permanent_link = f"tg://user?id={user_id}"

    # Add user to active users list
    active_users.add(user_id)

    # Check if user is in the channel
    if not await is_user_in_channel(user_id):
        await event.reply(
            f"Heya **[{full_name}]**({permanent_link}) Must Join Our Premium Channel To Use This Bot",
            buttons=[Button.url("JOIN HERE", f"https://t.me/pvtshits")]
        )
        return

    # Notify Admin Once
    if user_id not in notified_users:
        notified_users.add(user_id)
        total_users = len(active_users)
        await bot.send_message(
            ADMIN_USERNAME,
            f"🔔 **Gotta New User**\n\n"
            f"👤 **Name:** [{full_name}]({permanent_link})\n"
            f"📛 **Username:** @{username if username != 'No Username' else 'No Username'}\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"🔗 **Profile Link:** [Click Here]({permanent_link})\n"
            f"👥 **Total Users:** {total_users}",
            link_preview=False
        )
    
    # Inform User
    user_reporting[user_id] = {'status': 'idle'}
    await event.reply("✅️Omfo Chigga; You've Joined Our Channel So Now You Can Send /report Here To Start Reporting Your Target😈.")

# Report Command
@bot.on(events.NewMessage(pattern='/report'))
async def report_command(event):
    user_id = event.sender_id
    if not await is_user_in_channel(user_id):
        await event.reply(
            f"😶‍🌫️Heya **[{full_name}]**({permanent_link}) Must Joine Our Premium Channel To Use This Bot",
            buttons=[Button.url("JOIN HERE", f"https://t.me/pvtshits")]
        )
        return

    if user_reporting[user_id]['status'] != 'idle':
        await event.reply("⚠️ Bruhh You Have a Report in Process Finish That First🌷.")
        return

    user_reporting[user_id]['status'] = 'awaiting_username'
    await event.reply("⚠️ Note : Banning an Instagram Account isn't a Child's Play it can Take a Long Process so don't Loose Your Patience and don't Report the ID which is Patched **[Developer]**(https://t.me/Fictional_RJ):")

# Handle Username Submission
@bot.on(events.NewMessage)
async def handle_username(event):
    user_id = event.sender_id
    if user_reporting.get(user_id, {}).get('status') == 'awaiting_username':
        username = event.text.strip()
        if not username.startswith('@'):
            await event.reply("👤 Send The Username of Your Target (with @).")
            return

        # Add Instagram link to the username in Markdown format
        instagram_link = f"[{username}](http://instagram.com/{username[1:]})"  # Remove @ for the URL
        user_reporting[user_id] = {'status': 'reporting', 'username': username, 'count': 0, 'link': instagram_link}

        await event.reply(
            f"✅ Username `{username}` Accepted. Instagram Link: {instagram_link}. Shall We Start Reporting¿?",
            buttons=[
                [Button.inline("Start Reporting", b'start_reporting')],
                [Button.inline("Cancel", b'cancel_reporting')]
            ]
        )

# Handle Inline Buttons
@bot.on(events.CallbackQuery)
async def callback(event):
    user_id = event.sender_id
    if event.data == b'start_reporting':
        if user_reporting[user_id]['status'] != 'reporting':
            await event.answer("❌ Invalid action.", alert=True)
            return
        await start_reporting(event)
    elif event.data == b'cancel_reporting':
        user_reporting[user_id]['status'] = 'idle'
        await event.edit("❌ Reporting Process Has Been Cancelled.")
    elif event.data == b'stop_reporting':
        user_reporting[user_id]['status'] = 'idle'
        username = user_reporting[user_id].get('username', 'Unknown')
        instagram_link = user_reporting[user_id].get('link', 'Unknown link')
        await event.edit(f"🛑 Reporting {instagram_link} Has Been Stopped. Total Reports: {user_reporting[user_id]['count']}.")

# Reporting Function
async def start_reporting(event):
    user_id = event.sender_id
    instagram_link = user_reporting[user_id]['link']

    # Initialize reporting message
    message = await event.edit(
        f"🚀 Reporting {instagram_link}...",
        buttons=[[Button.inline("Stop Reporting", b'stop_reporting')]]
    )

    # Reporting loop (send reports every second, incrementing each second)
    for i in range(1, 10001):  # Extend to 10000 reports
        # Stop reporting if user presses the "Stop Reporting" button
        if user_reporting[user_id]['status'] != 'reporting':
            await message.edit(
                f"‼️ Reporting {instagram_link} Has Been Stopped. Total reports: {i}.",
                buttons=None  # Properly remove buttons
            )
            return

        # Update reporting count
        user_reporting[user_id]['count'] = i
        await message.edit(
            f"✅ Reported {instagram_link} {i} Times.",
            buttons=[[Button.inline("🛑 Stop Reporting", b'stop_reporting')]]
        )

        # Random notification after every 2,000 reports
        if i % 2000 == 0:
            if random.choice([True, False]):  # Randomize whether to notify
                await event.reply(f"🔔 Reporting {instagram_link}: {i} Reports Completed!")

        await asyncio.sleep(1)  # Wait for 1 second before the next report

    # Final notification when 10,000 reports are completed
    await message.edit(
        f"✅ Reporting {instagram_link} Complete (10,000 times).",
        buttons=None  # Properly remove buttons
    )
    await event.reply(f"🎉 **Congratulations!** {instagram_link} Reporting is Now Complete (10,000 times) But If Your Target Didn't Banned Yet You Can Start Reporting Again Otey.")

# Broadcast Command
@bot.on(events.NewMessage(pattern='/broadcast'))
async def broadcast(event):
    global broadcasting, waiting_for_broadcast_message, broadcast_message_content

    user_id = event.sender_id

    # Fetch the sender's entity
    sender = await bot.get_entity(user_id)
    sender_username = sender.username

    # Check if the sender is admin by comparing with ADMIN_USERNAME or ADMIN_ID
    if sender_username != ADMIN_USERNAME and user_id != ADMIN_ID:
        await event.reply("❌ Only Bot Admins Can Use This Command Niggah.")
        return

    # Set flag for broadcasting
    broadcasting = True
    waiting_for_broadcast_message = user_id  # Track that admin is being asked to send a message

    # Notify admin that the bot is ready to receive the message
    await event.reply("📝 Now Send The Message You Want to Broadcast to All Bot Users.")

# Handle Admin Message for Broadcast
@bot.on(events.NewMessage)
async def capture_admin_message(admin_event):
    global broadcasting, waiting_for_broadcast_message, broadcast_message_content

    user_id = admin_event.sender_id

    # Fetch the sender's entity
    sender = await bot.get_entity(user_id)
    sender_username = sender.username

    # Check if the sender is the admin and broadcasting flag is set
    if broadcasting and waiting_for_broadcast_message == user_id and (
        sender_username == ADMIN_USERNAME or user_id == ADMIN_ID
    ):
        broadcast_message = admin_event.text.strip()

        # Validate the broadcast message
        if not broadcast_message or broadcast_message == '/broadcast':
            await admin_event.reply("❌ Broadcast Message Can't Be Empty, Try Again.")
            return

        # Ask the admin for confirmation
        broadcast_message_content = broadcast_message
        broadcasting = False  # Reset the broadcasting flag to avoid conflicts
        waiting_for_broadcast_message = None  # Reset waiting admin ID
        await admin_event.reply(
            f"💬 Do You Want To Broadcast This Message:\n\n{broadcast_message}\n\nConfirm karein:",
            buttons=[
                [Button.inline("Yeahh", b'confirm_yes')],
                [Button.inline("Nopes", b'confirm_no')]
            ]
        )

# Handle Broadcast Confirmation (Yes/No)
@bot.on(events.CallbackQuery)
async def handle_broadcast_confirmation(event):
    global broadcast_message_content

    user_id = event.sender_id

    # Fetch the sender's entity
    sender = await bot.get_entity(user_id)
    sender_username = sender.username

    # Ensure only admin can confirm the broadcast
    if sender_username != ADMIN_USERNAME and user_id != ADMIN_ID:
        await event.answer("❌ Only Bot Admin Can Give Confirmation Bruhh.", alert=True)
        return

    if event.data == b'confirm_yes':
        if not broadcast_message_content:
            await event.answer("❌ Invalid Broadcast Message.", alert=True)
            return

        failed = 0
        sent = 0  # Counter for successfully sent messages

        # Notify admin about the progress
        progress_message = await event.edit(f"📤 Starting Broadcast...\n\n👥 Total users: {len(active_users)}")

        # Send the broadcast message to all users
        for idx, user_id in enumerate(active_users, start=1):
            try:
                await bot.send_message(user_id, broadcast_message_content)
                sent += 1
            except Exception:
                failed += 1

            # Update progress to admin every 10 users
            if idx % 10 == 0 or idx == len(active_users):
                await progress_message.edit(
                    f"📤 Broadcasting...\n\n✅ Sent: {sent}\n❌ Failed: {failed}\n👥 Remaining: {len(active_users) - idx}"
                )

        # Notify admin that broadcast is complete
        await progress_message.edit(
            f"✅ Broadcast Completed!\n\n📤 Sent to: {sent} users\n❌ Failed: {failed}\n👥 Total users: {len(active_users)}"
        )

        # Reset the broadcast message content
        broadcast_message_content = None

    elif event.data == b'confirm_no':
        # If the admin presses 'No', cancel the broadcast
        await event.edit("❌ Broadcast cancelled.")
        broadcast_message_content = None

# Run the Bot
print("🤖 Bot is running...")
bot.run_until_disconnected()