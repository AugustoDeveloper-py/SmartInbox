# SmartInbox

SmartInbox is a powerful command-line interface (CLI) tool for efficiently managing your Gmail inbox. It provides an intuitive way to handle unread emails, offering features like bulk actions, smart filtering, and quick responses - all from your terminal.

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Gmail API](https://img.shields.io/badge/Gmail-API-red)


## 🚀 Features

- **Smart Email Management**
  - View and manage unread emails efficiently
  - Bulk select/deselect functionality
  - Mark multiple emails as read with a single command
  - Quick reply functionality

- **Advanced Filtering**
  - Filter emails by time range (last X hours)
  - Search through subjects and senders
  - Clear filters with a single command

- **Data Export**
  - Export selected emails to CSV format
  - Customizable export with relevant email metadata

- **User-Friendly Interface**
  - Color-coded terminal interface
  - Intuitive command system
  - Real-time feedback on actions
  - Clear visibility of selected items

## 📋 Prerequisites

- Python 3.9 or higher
- Google account with Gmail
- Gmail API credentials

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SmartInbox.git
   cd SmartInbox
   ```

2. Install required packages:
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

3. Set up Gmail API credentials:
   - Visit the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API
   - Create credentials (OAuth 2.0 Client ID)
   - Download the credentials and save as `credentials.json` in the project directory

## 🎮 Usage

1. Run the application:
   ```bash
   python smartinbox.py
   ```

2. Available commands:
   - Enter number (e.g., `1`): Select/deselect specific email
   - `a`: Select all emails
   - `d`: Deselect all emails
   - `m`: Mark selected emails as read
   - `e`: Export selected emails to CSV
   - `r`: Refresh email list
   - `h <number>`: Filter by hours (e.g., `h 24`)
   - `s <text>`: Search in sender/subject
   - `p <number>`: Reply to specific email
   - `c`: Clear all filters
   - `q`: Quit application

## 🔐 Authentication

The first time you run the application, it will:
1. Open your default browser
2. Ask you to log in to your Google account
3. Request permission to access your Gmail
4. Store the authentication token locally for future use

## 🛠️ Technical Details

- Uses Gmail API v1
- Implements OAuth 2.0 authentication
- Stores authentication tokens in `token.pickle`
- Supports timezone-aware email dating
- Implements rate limiting for API calls

## 📦 Project Structure

```plaintext
SmartInbox/
├── smartinbox.py      # Main application file
├── credentials.json   # Gmail API credentials
├── token.pickle      # Stored authentication tokens
├── README.md         # Documentation
└── requirements.txt  # Python dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gmail API Team for the excellent API documentation
- Python community for the amazing libraries
- All contributors who help improve this project

## ⚠️ Security Note

- Never commit your `credentials.json` or `token.pickle` files
- Add them to your `.gitignore`
- Keep your API credentials secure

## 📧 Contact

For questions, suggestions, or issues, please open an issue in the GitHub repository.

## 🔄 Version History

- 1.0.0
  - Initial release
  - Basic email management functionality
  - Filtering and search capabilities
