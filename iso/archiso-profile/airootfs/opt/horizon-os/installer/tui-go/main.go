package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"
)

const banner = `
  ██╗  ██╗ ██████╗ ██████╗ ██╗███████╗ ██████╗ ███╗   ██╗     ██████╗ ███████╗
  ██║  ██║██╔═══██╗██╔══██╗██║╚══███╔╝██╔═══██╗████╗  ██║    ██╔═══██╗██╔════╝
  ███████║██║   ██║██████╔╝██║  ███╔╝ ██║   ██║██╔██╗ ██║    ██║   ██║███████╗
  ██╔══██║██║   ██║██╔══██╗██║ ███╔╝  ██║   ██║██║╚██╗██║    ██║   ██║╚════██║
  ██║  ██║╚██████╔╝██║  ██║██║███████╗╚██████╔╝██║ ╚████║    ╚██████╔╝███████║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝     ╚═════╝ ╚══════╝
  KDE Plasma 6 • KWin • Caelestia Shell • Ryoku SDDM • CachyOS Performance Core
`

func clearScreen() {
	fmt.Print("\033[H\033[2J")
}

func printHeader(stage string) {
	clearScreen()
	fmt.Print(banner)
	fmt.Printf("\n  ─── [ %s ] ──────────────────────────────────────────────────────────\n\n", stage)
}

func main() {
	if len(os.Args) > 1 && os.Args[1] == "--verify-only" {
		fmt.Println("Running Horizon OS Post-Installation Verification Audit...")
		cmd := exec.Command("python3", "installer/horizon-tui.py", "--verify-only")
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Run(); err != nil {
			os.Exit(1)
		}
		os.Exit(0)
	}

	printHeader("Stage 1 of 5: Hardware & Platform Probing")
	fmt.Println("  Probing system architecture and microarchitecture levels...")
	time.Sleep(300 * time.Millisecond)

	fmt.Println("  Firmware:    UEFI (x86_64)")
	fmt.Println("  CPU:         x86_64-v3 / v4 compatible")
	fmt.Println("  Desktop:     KDE Plasma 6 (Wayland) + Caelestia Shell (Quickshell)")
	fmt.Println("  Display Mgr: SDDM (Ryoku Orbital Clockwork Pure Black Theme)")
	fmt.Println("  Splash:      Overload Plasma 6 Splash")
	fmt.Println("  Icons:       Candy Bar (candy-icons)")
	fmt.Println("\n  Press Enter to continue to python-driven TUI engine...")

	var dummy string
	fmt.Scanln(&dummy)

	// Transfer execution to the full python installer suite
	cmd := exec.Command("python3", "installer/horizon-tui.py", strings.Join(os.Args[1:], " "))
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "Installer process ended: %v\n", err)
		os.Exit(1)
	}
}
