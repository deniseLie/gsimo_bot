const TelegramBot = require('node-telegram-bot-api')
const { google } = require('googleapis')

const bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true })

// Send a poll for attendance
const options = ['Group 1', 'Group 2', 'Group 3']

console.log('bottoken', process.env.BOT_TOKEN)
// Function to send the poll
const sendAttendancePoll = () => {
    // bot.sendPoll(process.env.CHAT_ID, 'Practice for tomorrow', options, {
    //     allows_multiple_answers: false,
    //     is_anonymous: false
    // });
    console.log('Attendance poll sent')
}
// sendAttendancePoll();

// Schedule task storage (user-defined times)
let scheduledTask = null;

// Send recurring scheduled poll
const sendRecurringScheduledPoll = () => {
    bot.onText(/\/schedule_poll (.+)/, (msg, match) => {
        const chatId = msg.chat.id
        const timePattern = match[1]

        // Validate cron syntax
        if (!cron.validate(timePattern)) {
            bot.sendMessage(chatId, 'Invalid cron pattern! Example: `0 9 * * *` for 9 AM daily.');
            return;
        }

        // Stop previous task if any
        if (scheduledTask) scheduledTask.stop();

        // Schedule the new poll
        scheduledTask = cron.schedule(timePattern, () => {
            sendAttendancePoll();
        });

        bot.sendMessage(chatId, `Poll scheduled successfully with pattern: \`${timePattern}\``);
    });
}

// Receive result
const retrieveResult = () => {
  bot.on('poll_answer', async (pollAnswer) => {
      const userId = pollAnswer.user.id;
      const userName = `${pollAnswer.user.first_name} ${pollAnswer.user.last_name || ''}`;
      const optionChosen = orchestraSections[pollAnswer.option_ids[0]];
    
      console.log(`User ${userName} (${userId}) chose: ${optionChosen}`);
    
      // Send data to Google Sheets
      await sendToGoogleSheets(userName, optionChosen);
  });
}

// Send to google sheet
const credentials = process.env.GOOGLE_API_CREDENTIALS; // Your Google API credentials
const SHEET_ID = 'YOUR_GOOGLE_SHEET_ID';

async function sendToGoogleSheets(userName, section) {
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });

  const sheets = google.sheets({ version: 'v4', auth: await auth.getClient() });

  const values = [[new Date().toISOString(), userName, section]];

  await sheets.spreadsheets.values.append({
    spreadsheetId: SHEET_ID,
    range: 'Attendance!A:C', // Target sheet range
    valueInputOption: 'RAW',
    resource: { values },
  });

  console.log('Attendance recorded in Google Sheets.');
}
