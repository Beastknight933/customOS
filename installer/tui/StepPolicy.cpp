#include "StepPolicy.hpp"

namespace {
bool answer_is_true(const std::map<std::string, std::string> &answers,
                    const char *name) {
  const auto it = answers.find(name);
  return it != answers.end() && it->second == "true";
}
} // namespace

namespace StepPolicy {
bool is_skipped(const std::string &step_name,
                const std::map<std::string, std::string> &answers) {
  std::string profile = "desktop-lockscreen";
  auto it_prof = answers.find("INSTALL_PROFILE");
  if (it_prof != answers.end() && !it_prof->second.empty()) {
    profile = it_prof->second;
  }

  bool install_shell = true;
  bool install_lockscreen = true;
  bool install_sddm = false;

  if (profile == "desktop") {
    install_shell = true;
    install_lockscreen = false;
    install_sddm = false;
  } else if (profile == "desktop-lockscreen") {
    install_shell = true;
    install_lockscreen = true;
    install_sddm = false;
  } else if (profile == "full") {
    install_shell = true;
    install_lockscreen = true;
    install_sddm = true;
  } else if (profile == "custom") {
    install_shell = answer_is_true(answers, "INSTALL_SHELL");
    install_lockscreen = answer_is_true(answers, "APPLY_LOCKSCREEN");
    install_sddm = answer_is_true(answers, "INSTALL_SDDM");
  }

  if (step_name == "Update system") {
    return answer_is_true(answers, "SKIP_SYSTEM_UPDATE");
  }
  if (step_name == "Configure lock screen") {
    return !install_lockscreen;
  }
  if (step_name == "Install SDDM theme") {
    return !install_sddm;
  }
  if (step_name == "Deploy config files" ||
      step_name == "Deploy session environment" ||
      step_name == "Build Aetherium shell" ||
      step_name == "Create autostart entries") {
    return !install_shell;
  }
  return false;
}
} // namespace StepPolicy
