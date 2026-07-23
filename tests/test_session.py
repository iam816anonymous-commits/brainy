from brain.context.session import ContextSessionManager

def test_session_manager_flow():
    ContextSessionManager.clear()

    # 1. Create sessions
    sess1 = ContextSessionManager.create_session(
        project="SessProj",
        goal="Migrate schema",
        current_task="Add indexes",
        active_files=["db.py", "models.py"],
        branch="feature/schema"
    )

    assert sess1.id is not None
    assert sess1.project == "SessProj"
    assert sess1.current_task == "Add indexes"

    # 2. Get session
    retrieved = ContextSessionManager.get_session(sess1.id)
    assert retrieved is not None
    assert retrieved.id == sess1.id

    # 3. Add checkpoint
    ContextSessionManager.add_checkpoint(sess1.id, "Index completed", "Added btree indexes to objects")

    updated = ContextSessionManager.get_session(sess1.id)
    assert len(updated.checkpoints) == 1
    assert updated.checkpoints[0]["name"] == "Index completed"

    # 4. List sessions
    all_sess = ContextSessionManager.list_sessions(project="SessProj")
    assert len(all_sess) == 1

    all_sess_mismatch = ContextSessionManager.list_sessions(project="OtherProj")
    assert len(all_sess_mismatch) == 0
