import os
import random
import logging
import telegram
import texts
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main.py')


def random_nums():
    res = ''
    for i in range(13):
        res += str(random.randint(0, 9))
    return res


def start_hello(update: Update, context: CallbackContext):
    update.message.reply_text(texts.hello().format(update.effective_user.id), parse_mode=telegram.ParseMode.MARKDOWN)


def start(update: Update, context: CallbackContext):
    if len(context.args) == 1:
        logger.info(f'{update.message.from_user.full_name}({update.message.from_user.link}) '
                    f'захотел(а) написать ему: {context.args[0]}')

        context.user_data['Valentine'] = True
        context.user_data['Recipient'] = context.args[0]
        context.user_data['SenderLink'] = update.message.from_user.link

        update.message.reply_text(texts.start(), parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        logger.info(f'{update.message.from_user.full_name}({update.message.from_user.link}) '
                    f'ввел(а) /start без айдишника')

        clear_vars(context)
        start_hello(update, context)


def any_msg(update: Update, context: CallbackContext):
    if 'Valentine' in context.user_data and context.user_data['Valentine']:
        recipient = context.user_data['Recipient']
        link = context.user_data['SenderLink']
    else:
        recipient = update.effective_user.id
        link = update.message.from_user.link
    logger.info(f'{update.message.from_user.full_name}({link}) '
                f'отправил(а) сообщение "{update.message.text}" ему: {recipient}')

    context.bot.sendMessage(recipient,
                            f'У вас новое анонимное признание ([#]({link}){random_nums()}):\n\n*{update.message.text}*',
                            parse_mode=telegram.ParseMode.MARKDOWN,
                            disable_web_page_preview=True)
    update.message.reply_text(texts.done().format(update.effective_user.id), parse_mode=telegram.ParseMode.MARKDOWN)

    clear_vars(context)


def clear_vars(context: CallbackContext):
    context.user_data['Valentine'] = False
    context.user_data['Recipient'] = ''
    context.user_data['SenderLink'] = ''


def main() -> None:
    updater = Updater(os.environ.get('BOT_API'))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, any_msg))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
