"""Generate an Xcode project with Python 3 (no XcodeGen dependency)."""
from hashlib import sha1
from pathlib import Path
import json

root = Path(__file__).resolve().parent
def uid(name):
    return sha1(name.encode()).hexdigest()[:24].upper()
def quote(value):
    return json.dumps(str(value), ensure_ascii=False)
objects = []
def obj(name, body):
    objects.append(f"{uid(name)} = {{ {body} }};")
def refs(names):
    return "(" + ", ".join(uid(name) for name in names) + ",)"

sources = sorted(root.glob("Sources/**/*.swift"))
source_names = [str(p.relative_to(root)) for p in sources]
for path in source_names:
    obj(path, f"isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = {quote(path)}; sourceTree = SOURCE_ROOT;")
    obj("build:" + path, f"isa = PBXBuildFile; fileRef = {uid(path)};")
obj("product", 'isa = PBXFileReference; explicitFileType = wrapper.application; path = MetaBookReader.app; sourceTree = BUILT_PRODUCTS_DIR;')
obj("products", f"isa = PBXGroup; children = {refs(['product'])}; name = Products; sourceTree = \"<group>\";")
obj("main", f"isa = PBXGroup; children = {refs(source_names + ['products'])}; sourceTree = \"<group>\";")
obj("sources", f"isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; files = {refs(['build:' + p for p in source_names])}; runOnlyForDeploymentPostprocessing = 0;")
obj("resources", "isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; files = (); runOnlyForDeploymentPostprocessing = 0;")
products = ["MWDATCore", "MWDATCamera"]
for product in products:
    obj(product, f"isa = XCSwiftPackageProductDependency; package = {uid('package')}; productName = {product};")
    obj("framework:" + product, f"isa = PBXBuildFile; productRef = {uid(product)};")
obj("frameworks", f"isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = {refs(['framework:' + p for p in products])}; runOnlyForDeploymentPostprocessing = 0;")
obj("package", 'isa = XCRemoteSwiftPackageReference; repositoryURL = "https://github.com/facebook/meta-wearables-dat-ios"; requirement = { kind = exactVersion; version = 1.0.0; };')
for mode in ("Debug", "Release"):
    project_settings = {
        "CLANG_ENABLE_MODULES": "YES", "SDKROOT": "iphoneos",
        "IPHONEOS_DEPLOYMENT_TARGET": "17.2", "SWIFT_VERSION": "6.3",
        "SWIFT_STRICT_CONCURRENCY": "complete",
        "SWIFT_OPTIMIZATION_LEVEL": "-Onone" if mode == "Debug" else "-O",
        "DEBUG_INFORMATION_FORMAT": "dwarf" if mode == "Debug" else "dwarf-with-dsym",
        "SWIFT_ACTIVE_COMPILATION_CONDITIONS": "DEBUG" if mode == "Debug" else "",
    }
    target_settings = {
        "PRODUCT_NAME": "MetaBookReader", "PRODUCT_BUNDLE_IDENTIFIER": "com.example.metabookreader",
        "INFOPLIST_FILE": "Sources/Info.plist", "GENERATE_INFOPLIST_FILE": "NO",
        "CODE_SIGN_STYLE": "Automatic", "DEVELOPMENT_TEAM": "",
        "CURRENT_PROJECT_VERSION": "1", "MARKETING_VERSION": "0.1.0",
        "TARGETED_DEVICE_FAMILY": "1", "META_APP_ID": "0", "CLIENT_TOKEN": "",
        "LD_RUNPATH_SEARCH_PATHS": "$(inherited) @executable_path/Frameworks",
    }
    for kind, settings in (("project", project_settings), ("target", target_settings)):
        values = " ".join(f"{key} = {quote(value)};" for key, value in settings.items())
        obj(kind + mode, f"isa = XCBuildConfiguration; name = {mode}; buildSettings = {{ {values} }};")
for kind in ("project", "target"):
    obj(kind + "configs", f"isa = XCConfigurationList; buildConfigurations = {refs([kind + 'Debug', kind + 'Release'])}; defaultConfigurationIsVisible = 0; defaultConfigurationName = Release;")
obj("target", f"isa = PBXNativeTarget; name = MetaBookReader; productName = MetaBookReader; productReference = {uid('product')}; productType = \"com.apple.product-type.application\"; buildConfigurationList = {uid('targetconfigs')}; buildPhases = {refs(['sources', 'frameworks', 'resources'])}; buildRules = (); dependencies = (); packageProductDependencies = {refs(products)};")
obj("project", f"isa = PBXProject; attributes = {{ LastUpgradeCheck = 2640; }}; buildConfigurationList = {uid('projectconfigs')}; compatibilityVersion = \"Xcode 14.0\"; developmentRegion = en; knownRegions = (en, Base, ja); mainGroup = {uid('main')}; productRefGroup = {uid('products')}; projectDirPath = \"\"; projectRoot = \"\"; targets = {refs(['target'])}; packageReferences = {refs(['package'])};")
directory = root / "MetaBookReader.xcodeproj"
directory.mkdir(exist_ok=True)
directory.joinpath("project.pbxproj").write_text(
    "// !$*UTF8*$!\n{ archiveVersion = 1; classes = {}; objectVersion = 56; objects = {\n"
    + "\n".join(objects) + f"\n}}; rootObject = {uid('project')}; }}\n"
)
scheme_dir = directory / "xcshareddata/xcschemes"
scheme_dir.mkdir(parents=True, exist_ok=True)
reference = f'<BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{uid("target")}" BuildableName="MetaBookReader.app" BlueprintName="MetaBookReader" ReferencedContainer="container:MetaBookReader.xcodeproj"/>'
scheme_dir.joinpath("MetaBookReader.xcscheme").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<Scheme LastUpgradeVersion="2640" version="1.3">'
    '<BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries>'
    '<BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES">'
    + reference + '</BuildActionEntry></BuildActionEntries></BuildAction>'
    '<LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" allowLocationSimulation="YES">'
    '<BuildableProductRunnable runnableDebuggingMode="0">' + reference + '</BuildableProductRunnable></LaunchAction>'
    '<ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES">'
    '<BuildableProductRunnable runnableDebuggingMode="0">' + reference + '</BuildableProductRunnable></ProfileAction>'
    '<AnalyzeAction buildConfiguration="Debug"/><ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/></Scheme>'
)
print(directory)
