package common

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"regexp"
	"runtime"

	"github.com/Omar-Mhd-Fadi-Zaraa/TuxTailor/config"
	"github.com/joho/godotenv"
)

/* Get environment variables */
func GetEnv() string {
	return config.APP_INFO["env"]
}

func GetBasePath() string {
	env := GetEnv()
	fmt.Println("Environment:", env)
	if env == "" {
		env = "dev" // Default to development environment
	}

	if env == "dev" {
		return "data"
	}
	// Get the base storage path suitable for the current operating system
	var basePath string
	switch runtime.GOOS {
	case "windows":
		appData := os.Getenv("APPDATA")
		if appData == "" {
			appData = filepath.Join(os.Getenv("USERPROFILE"), "AppData", "Roaming")
		}
		basePath = filepath.Join(appData, "tuxtailor")
	default: // Linux and other Unix-like systems
		basePath = "/var/lib/transok"
		// If not root, use user directory
		if os.Getuid() != 0 {
			homeDir, _ := os.UserHomeDir()
			basePath = filepath.Join(homeDir, ".tailor")
		}
	}

	return basePath
}

func LoadEnvFile() error {
	err := godotenv.Load(".env")
	return err
}

func GetPythonScripts() ([]string, error) {
	pyRegex := regexp.MustCompile(`\.py$`)

	err := LoadEnvFile()
	if err != nil {
		return nil, err
	}

	var pyFiles []string
	scritpsDir := os.Getenv("PYTHON_SCRIPTS")
	err = filepath.WalkDir(scritpsDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.Name() == ".venv" {
			return filepath.SkipDir
		}
		if !d.IsDir() && pyRegex.Match([]byte(d.Name())) {
			pyFiles = append(pyFiles, d.Name())
		}
		return nil
	})

	if err != nil {
		return nil, err
	}

	return pyFiles, nil
}
