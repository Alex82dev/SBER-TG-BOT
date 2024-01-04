#ifndef TELEGRAM_BOT_H
#define TELEGRAM_BOT_H

#include <string>
#include <vector>

// Define a struct to represent a Telegram message
struct TelegramMessage {
    std::string text;
    std::string chatId;
};

// Define the TelegramBot class
class TelegramBot {
public:
    // Constructor
    TelegramBot(const std::string& token);

    // Method to send a text message
    void sendMessage(const std::string& chatId, const std::string& text);

    // Method to process incoming updates
    void processUpdates();

private:
    std::string botToken;
    std::vector<TelegramMessage> messageQueue;

    // Method to handle an incoming message
    void handleMessage(const TelegramMessage& message);

    // Method to send a request to the Telegram API
    std::string sendRequest(const std::string& method, const std::string& parameters);
};

#endif  // TELEGRAM_BOT_H
