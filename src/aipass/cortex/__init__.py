"""AIPass Cortex — Branch Creation & Template Engine.

Creates new branches (agent workspaces) following a 7-step flow:
    1. Validate template — verify template directory exists
    2. Extract metadata — branch name, profile, git repo from path
    3. Build placeholders — replacement dict: {{BRANCHNAME}}, {{CWD}}, {{DATE}}, etc.
    4. Smart file rename — rename existing memory files to standard convention
    5. Copy template — copy entire template, replace placeholders in text files
    6. File renaming — LOCAL.json -> BRANCHNAME.local.json, etc.
    7. Registry entry — add to BRANCH_REGISTRY.json + fire trigger event

Three template types:
    - branch_template/         — standard dev branch (apps/, modules/, handlers/, tests/)
    - business_branch_template/ — business branch (playbooks/, strategy/, research/)
    - team_template/           — think-tank manager (research/, ideas/, decisions/)

Accessed through drone: `drone @cortex create`, NOT standalone.

Architecture reference: vera/projects/framework/architecture_reference.md §5

Status: PLACEHOLDER — not yet implemented.
"""
