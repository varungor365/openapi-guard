from openapi_guard.cli import compare


def test_removed_operation_is_breaking():
    old = {"paths": {"/users": {"get": {"responses": {"200": {}}}}}}
    new = {"paths": {}}
    changes = compare(old, new)
    assert any(item.kind == "removed-operation" and item.level == "breaking" for item in changes)


def test_new_required_parameter_is_breaking():
    old = {"paths": {"/users": {"get": {"parameters": [], "responses": {"200": {}}}}}}
    new = {"paths": {"/users": {"get": {"parameters": [{"in": "query", "name": "tenant", "required": True}], "responses": {"200": {}}}}}}
    changes = compare(old, new)
    assert any(item.kind == "new-required-parameter" for item in changes)


def test_added_operation_is_non_breaking():
    changes = compare({"paths": {}}, {"paths": {"/health": {"get": {"responses": {"200": {}}}}}})
    assert changes[0].level == "non-breaking"
