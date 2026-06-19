package config



var APP_INFO = map[string]string{
	"name":    "TuxTailor",
	"version": "0.0.0",
	"env":     "prod",
	"desc":    "An agentic Linux ISO/container file/VM file compiler",
	"author":  "Omar-Mhd-Fadi-Zaraa",
	"email":   "o.zarraa.2005@gmail.com",
}

// For logging errors
const (
	ENABLE_LOG   = true // enable logging by default
	LOG_MAX_SIZE = 100  // maximum size of each log file in (MB)
	LOG_BACKUPS  = 3    // number of log files to keep
	LOG_MAX_AGE  = 15   // number of days to keep a log file
)
