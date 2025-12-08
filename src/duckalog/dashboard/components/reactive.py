"""Reactive components using Datastar for real-time updates."""

from __future__ import annotations

from ..datastar_integration import ds


def reactive_status_indicator(signal_name: str = "buildStatus") -> str:
    """Create a reactive status indicator with different visual states."""
    return f"""
        <div {ds.signals({'buildStatus': 'idle', 'buildProgress': 0})}
             {ds.class_({
                 'status-indicator': True,
                 'status-idle': f'${signal_name} === "idle"',
                 'status-building': f'${signal_name} === "building"',
                 'status-success': f'${signal_name} === "success"',
                 'status-error': f'${signal_name} === "error"'
             })}
             {ds.show(f'${signal_name} !== "idle"')}
             style="
                 padding: 8px 16px;
                 border-radius: 20px;
                 font-size: 14px;
                 font-weight: 500;
                 transition: all 0.3s ease;
             ">
            <span {ds.text(f'${signal_name}')}></span>
            <div {ds.show(f'${signal_name} === "building"')}
                 style="width: 100px; height: 4px; background: #eee; border-radius: 2px; margin-top: 8px;">
                <div {ds.class_({
                    'progress-bar': True,
                    'progress-active': f'${signal_name} === "building"'
                })}
                     {ds.html('style: `width: ${{{$buildProgress * 100}}%`')}
                     style="
                         height: 100%;
                         background: linear-gradient(90deg, #007bff, #0056b3);
                         border-radius: 2px;
                         transition: width 0.3s ease;
                     ">
                </div>
            </div>
        </div>
    """


def live_search_form(target_url: str = "/views") -> str:
    """Create a live search form that filters results in real-time."""
    return f"""
        <form {ds.signals({'searchQuery': '', 'searchResults': []})}>
            <div style="display: flex; gap: 8px; align-items: center;">
                <input {ds.bind('searchQuery')}
                       type="search"
                       placeholder="Search views..."
                       {ds.on('input', '$$get(`/views?q=${{$searchQuery}}`)')}
                       style="flex: 1; min-width: 200px;">
                <button type="button"
                        {ds.on('click', '$searchQuery = ""; $$get(`/views`)')}
                        {ds.show('$searchQuery !== ""')}
                        style="padding: 8px 16px;">
                    Clear
                </button>
            </div>
            <div {ds.show('$searchQuery !== ""')} style="margin-top: 8px; font-size: 14px; color: #666;">
                Searching for: <strong {ds.text('$searchQuery')}></strong>
            </div>
        </form>
    """


def reactive_query_editor() -> str:
    """Create a reactive SQL query editor with real-time execution status."""
    return f"""
        <div {ds.signals({
            'queryText': '',
            'queryStatus': 'idle',
            'queryResults': [],
            'queryError': '',
            'isExecuting': False
        })}>
            <div style="margin-bottom: 16px;">
                <label for="query-text">SQL Query:</label>
                <textarea {ds.bind('queryText')}
                          id="query-text"
                          rows="8"
                          placeholder="Enter your SQL query here..."
                          style="font-family: monospace; width: 100%;">
                </textarea>
            </div>

            <div style="display: flex; gap: 8px; margin-bottom: 16px;">
                <button {ds.on('click', '$isExecuting = true; $$post("/query", { body: JSON.stringify({sql: $queryText}) })')}
                        {ds.hide('$isExecuting')}
                        style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px;">
                    Execute Query
                </button>

                <button {ds.show('$isExecuting')}
                        disabled
                        style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px;">
                    Executing...
                </button>
            </div>

            <div {ds.show('$queryStatus === "error"')} style="margin-bottom: 16px;">
                <div style="background: #f8d7da; color: #721c24; padding: 12px; border-radius: 4px; border: 1px solid #f5c6cb;">
                    <strong>Error:</strong> <span {ds.text('$queryError')}></span>
                </div>
            </div>

            <div {ds.show('$queryStatus === "success" && $queryResults.length > 0')} style="margin-bottom: 16px;">
                <div style="background: #d4edda; color: #155724; padding: 12px; border-radius: 4px; border: 1px solid #c3e6cb;">
                    <strong>Success:</strong> Query executed successfully. <span {ds.text('$queryResults.length')}></span> rows returned.
                </div>
            </div>
        </div>
    """


def real_time_notification_center() -> str:
    """Create a real-time notification center that displays live notifications."""
    return f"""
        <div {ds.signals({'notifications': []})}
             {ds.execute('$$get("/events/notifications")')}
             style="position: fixed; top: 80px; right: 20px; z-index: 1000; max-width: 300px;">

            <!-- Notification container -->
            <div {ds.show('$notifications.length > 0')}
                 style="display: flex; flex-direction: column; gap: 8px;">

                <!-- Individual notifications -->
                <template {ds.bind('$notifications')}>
                    <div {ds.class_({
                        'notification': True,
                        'notification-info': '$type === "info"',
                        'notification-success': '$type === "success"',
                        'notification-warning': '$type === "warning"',
                        'notification-error': '$type === "error"'
                    })}
                         style="
                             padding: 12px 16px;
                             border-radius: 6px;
                             border-left: 4px solid;
                             background: white;
                             box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                             animation: slideIn 0.3s ease-out;
                         ">
                        <div style="font-weight: 500; margin-bottom: 4px;" {ds.text('$message')}></div>
                        <div style="font-size: 12px; color: #666;" {ds.text('$timestamp')}></div>
                    </div>
                </template>
            </div>
        </div>

        <style>
            @keyframes slideIn {{
                from {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
                to {{
                    transform: translateX(0);
                    opacity: 1;
                }}
            }}

            .notification-info {{ border-left-color: #007bff; }}
            .notification-success {{ border-left-color: #28a745; }}
            .notification-warning {{ border-left-color: #ffc107; }}
            .notification-error {{ border-left-color: #dc3545; }}
        </style>
    """


def build_status_card() -> str:
    """Create a real-time build status card."""
    return f"""
        <div {ds.signals({'buildStatus': 'idle', 'buildTime': '', 'buildProgress': 0})}
             {ds.execute('$$get("/events/build-status")')}>
            <article>
                <header>
                    <h3>Build Status</h3>
                    <div {ds.show('$buildStatus !== "idle"')}>
                        <small {ds.text('$buildTime')}></small>
                    </div>
                </header>

                <div style="display: flex; align-items: center; gap: 12px;">
                    <div {ds.class_({
                        'status-dot': True,
                        'status-idle': '$buildStatus === "idle"',
                        'status-building': '$buildStatus === "building"',
                        'status-success': '$buildStatus === "success"',
                        'status-error': '$buildStatus === "error"'
                    })}
                         style="
                             width: 12px;
                             height: 12px;
                             border-radius: 50%;
                             background: #6c757d;
                         ">
                    </div>

                    <div>
                        <div style="font-weight: 500;" {ds.text('$buildStatus')}></div>
                        <div {ds.show('$buildStatus === "building"')} style="font-size: 14px; color: #666;">
                            Building... <span {ds.text('Math.round($buildProgress * 100)')}></span>%
                        </div>
                    </div>
                </div>

                <div {ds.show('$buildStatus === "building"')} style="margin-top: 12px;">
                    <div style="width: 100%; height: 4px; background: #e9ecef; border-radius: 2px;">
                        <div {ds.html('style: `width: ${{$buildProgress * 100}}%`')}
                             style="
                                 height: 100%;
                                 background: linear-gradient(90deg, #007bff, #0056b3);
                                 border-radius: 2px;
                                 transition: width 0.3s ease;
                             ">
                        </div>
                    </div>
                </div>
            </article>

            <style>
                .status-idle {{ background: #6c757d; }}
                .status-building {{ background: #ffc107; animation: pulse 1.5s infinite; }}
                .status-success {{ background: #28a745; }}
                .status-error {{ background: #dc3545; }}

                @keyframes pulse {{
                    0%, 100% {{ opacity: 1; }}
                    50% {{ opacity: 0.5; }}
                }}
            </style>
        </div>
    """