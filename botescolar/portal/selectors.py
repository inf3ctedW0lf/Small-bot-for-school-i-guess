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

# Persistent subject filter panel (div[1] of the layout) — stays
# mounted while navigating between subjects, so subject N+1 can be
# clicked directly from subject N's page without returning to the
# dashboard first.
SUBJECT_FILTER_LINKS = (
    "/html/body/app-root/ng-component/ng-component/app-layout-legacy/"
    "app-layout-module/div/div/app-sidenav-group/div/div/div/div[1]/"
    "app-filter-subject/div/div[2]/a"
)

# ==========================================================
# CONTENT
# ==========================================================

CONTENT_CARD = (
    "/html/body/app-root/ng-component/ng-component/app-layout-legacy/"
    "app-layout-module/div/div/app-sidenav-group/div/div/div/div[2]/"
    "ng-component/div/ng-component/app-card/div/div"
)

RESOURCE_COMPONENT = "app-resource-component"

# Resource attachments live inside the "Aula" section (div[1]) of a card
RESOURCE_ITEMS = "./div[1]//app-resource-component"

# The "Atividade" (activity/assignment) section of a card
TASK_SECTION = "./div[2]"

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