# settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

Then run once:

PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
https://github.com/danyi1212/celery-insights/tree/main

```vmprofile
-Xms8g
-Xmx24g
-XX:ReservedCodeCacheSize=2g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=80
-XX:InitiatingHeapOccupancyPercent=30
-XX:G1HeapRegionSize=32m
-XX:+UseStringDeduplication
-XX:ParallelGCThreads=10
-XX:ConcGCThreads=5
-XX:CICompilerCount=4
-XX:SoftRefLRUPolicyMSPerMB=50
-XX:+HeapDumpOnOutOfMemoryError
-XX:-OmitStackTraceInFastThrow
-XX:MaxJavaStackTraceDepth=10000
-ea
-Dsun.io.useCanonCaches=false
-Djdk.http.auth.tunneling.disabledSchemes=""
-Djdk.attach.allowAttachSelf=true
-Djdk.module.illegalAccess.silent=true
-Dkotlinx.coroutines.debug=off
-Dide.no.platform.update=true
-Dide.quick.access.log=false
-Dide.performance.monitoring.enabled=false
-Dawt.toolkit.name=WLToolkit
-Dsun.java2d.uiScale=1.0
-Dsun.java2d.opengl=true
-Dsun.java2d.xrender=false
-Djava2d.font.loadFontConf=false
-Dide.experimental.ui=true

```
