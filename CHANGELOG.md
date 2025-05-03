# Pomodium Changelog

## Version 0.5 (2024-12-19)
- Settings now are saved (reported by Đỗ Xuân Đức Sơn)

## Version 0.4 (2024-12-17)
### Fixed
- Fixed long break not starting after completing the specified number of work sessions
  - The session count is now correctly maintained until the long break completes
  - Long break (15 minutes) now properly triggers after completing 2 work sessions
  - Added detailed logging for better debugging and session tracking
- Fixed configuration persistence across addon updates 
  - Now using Anki's addon manager for configuration management
  - Settings will now persist through addon updates

### Added
- Added debug logging to track session transitions and timer states
- Added changelog window to show recent updates when opening Anki
- Added option to control timer visibility during review sessions
  - Timer now stays visible by default during reviews
  - Added setting to optionally hide timer during reviews
