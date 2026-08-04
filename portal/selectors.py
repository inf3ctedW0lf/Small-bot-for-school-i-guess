"""
All portal selectors live here.

If the Adventista portal changes its HTML,
this should ideally be the only file requiring updates.
"""

# ======================================================
# Dashboard / Today
# ======================================================

DAY_BLOCK = (
    "/html/body/app-root/ng-component/"
    "ng-component/app-layout-legacy/"
    "app-layout-dashboard/div/"
    "app-sidenav-group/div/div/div/"
    "ng-component/div[2]/div[3]/"
    "app-day-subject-summary[1]/"
    "div/div/div[2]/div[2]/"
    "app-badge/span"
)

# ==========================================================
# SUBJECT SELECTION
# ==========================================================

# The modal containing subjects
SUBJECT_MODAL = (
    "//app-day-subject-summary"
)


# Subjects inside the modal
SUBJECT_LINKS = (
    ".//app-badge//span"
)

# ==========================================================
# CONTENT
# ==========================================================

CONTENT_CARD = (
    "/html/body/app-root/ng-component/ng-component/app-layout-legacy/app-layout-module/div/div/app-sidenav-group/div/div/div/div[2]"
)

RESOURCE_COMPONENT = "app-resource-component"

# ==========================================================
# RESOURCE DOWNLOAD
# ==========================================================

DOWNLOAD_BUTTON = ".//div/div[2]/div[2]/button[1]"

PDF_SAVE_BUTTON = '//*[@id="save"]'

# ==========================================================
# GENERAL
# ==========================================================

SUBJECT_IGNORE_TEXT = (
    "Ensino Fundamental",
)

# ==========================================================
# WAIT TIMES
# ==========================================================

DEFAULT_WAIT = 30

SHORT_WAIT = 5

LONG_WAIT = 60