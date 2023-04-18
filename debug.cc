#include <atomic>
#include <cstddef>
#include <functional>
#include <map>
#include <mutex>
#include <thread>

class Debug {
 public:
  static bool enabled_;

  static int get_indent(bool enter);

  static int short_tid();

  static void enable() { enabled_ = true; }

  static void disable() { enabled_ = false; }

  Debug(const char *fmt, ...) {
    char buf[1000];
    va_list args;
    va_start(args, fmt);
    vsnprintf(buf, 1000, fmt, args);
    va_end(args);
    msg_ = buf;

    myIndent_ = get_indent(/*enter=*/true);

    if (enabled_) {
      for (int i = 0; i < myIndent_; i++) {
        fprintf(stderr, " ");
      }
      fprintf(stderr, "> %s\n", msg_.c_str());
    }
  }

  Debug(std::function<void()> func) : func_(func) {}

  ~Debug() {
    if (enabled_) {
      if (func_) {
        func_();
      } else {
        for (int i = 0; i < myIndent_; i++) {
          fprintf(stderr, " ");
        }
        fprintf(stderr, "< %s%s\n", msg_.c_str(), note_.c_str());
      }
    }

    get_indent(/*enter=*/false);
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
  std::function<void()> func_;

  bool isFuncMsg() const { return msg_[msg_.size() - 1] == ')'; }
};

// In cc file:

bool Debug::enabled_ = true;

/*static*/
int Debug::get_indent(bool enter) {
  thread_local int indent{0};
  int v = indent;
  if (enter) {
    indent++;
  } else {
    indent--;
  }
  return v;
}

/*static*/
int Debug::short_tid() {
  static std::mutex mu;
  static std::map<std::thread::id, int> tids;

  std::lock_guard l{mu};
  auto tid = std::this_thread::get_id();
  if (!tids.contains(tid)) {
    tids[tid] = tids.size();
  }

  return tids[tid];
}
