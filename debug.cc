class Debug {
 public:
  static int curFuncIndent_;
  static int curCtorIndent_;
  static bool enabled_;

  static void enable() { enabled_ = true; }

  static void disable() { enabled_ = false; }

  Debug(const char *fmt, ...) {
    char buf[1000];
    va_list args;
    va_start(args, fmt);
    vsnprintf(buf, 1000, fmt, args);
    va_end(args);
    msg_ = buf;

    if (isFuncMsg()) {
      myIndent_ = curFuncIndent_++;
    } else {
      myIndent_ = curCtorIndent_++;
    }

    if (enabled_) {
      for (int i = 0; i < myIndent_; i++) {
        fprintf(stderr, " ");
      }
      fprintf(stderr, "> %s\n", msg_.c_str());
    }
  }

  ~Debug() {
    if (enabled_) {
      for (int i = 0; i < myIndent_; i++) {
        fprintf(stderr, " ");
      }
      fprintf(stderr, "< %s%s\n", msg_.c_str(), note_.c_str());
    }

    if (isFuncMsg()) {
      curFuncIndent_--;
    } else {
      curCtorIndent_--;
    }
  }

  void note(const char *fmt, ...) {
    char buf[1000];
    va_list args;
    va_start(args, fmt);
    if (enabled_) {
      vsnprintf(buf, 1000, fmt, args);
    }
    va_end(args);
    note_ = std::string{" // "} + buf;
  }

  void print(const char *fmt, ...) {
    char buf[1000];
    va_list args;
    va_start(args, fmt);
    if (enabled_) {
      vsnprintf(buf, 1000, fmt, args);
    }
    va_end(args);

    if (enabled_) {
      for (int i = 0; i < myIndent_; i++) {
        fprintf(stderr, " ");
      }
      fprintf(stderr, "- %s\n", buf);
    }
  }

 private:
  int myIndent_;
  std::string msg_;
  std::string note_;

  bool isFuncMsg() const { return msg_[msg_.size() - 1] == ')'; }
};

int Debug::curFuncIndent_ = 0;
int Debug::curCtorIndent_ = 40;
bool Debug::enabled_ = true;
