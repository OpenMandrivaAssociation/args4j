Name:		args4j
Version:	2.37
Release:	1
Summary:	Java command line arguments parser
Group:		Development/Java
License:	MIT
URL:		https://github.com/kohsuke/args4j
Source0:	https://github.com/kohsuke/args4j/archive/refs/tags/args4j-site-%{version}.tar.gz#/args4j-site-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven

%description
args4j parses command line options from annotations. 2.37 is the
current release. This build ships the library and args4j-tools. The
Maven plugin is not built. The tools jar launches the option-list
generator through javax.tools.JavaCompiler. The build targets Java 11
and skips tests. The automatic module names are args4j and args4j.tools.

%prep
%autosetup -n args4j-args4j-site-%{version}
python - <<'PY'
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def tag(name):
    return "{" + NS + "}" + name

def add(parent, name, text):
    node = ET.SubElement(parent, tag(name))
    node.text = text
    return node

def resources(build):
    box = ET.SubElement(build, tag("resources"))
    resource = ET.SubElement(box, tag("resource"))
    add(resource, "directory", "src")
    includes = ET.SubElement(resource, tag("includes"))
    add(includes, "include", "**/*.properties")
    add(includes, "include", "META-INF/services/*")

def jar_plugin(build, module_name, main_class):
    plugins = ET.SubElement(build, tag("plugins"))
    plugin = ET.SubElement(plugins, tag("plugin"))
    add(plugin, "groupId", "org.apache.maven.plugins")
    add(plugin, "artifactId", "maven-jar-plugin")
    add(plugin, "version", "3.3.0")
    configuration = ET.SubElement(plugin, tag("configuration"))
    archive = ET.SubElement(configuration, tag("archive"))
    if main_class:
        manifest = ET.SubElement(archive, tag("manifest"))
        add(manifest, "mainClass", main_class)
    entries = ET.SubElement(archive, tag("manifestEntries"))
    add(entries, "Automatic-Module-Name", module_name)
    return plugins

def project(artifact, module_name, main_class, depend_on_args4j):
    root = ET.Element(tag("project"))
    add(root, "modelVersion", "4.0.0")
    add(root, "groupId", "args4j")
    add(root, "artifactId", artifact)
    add(root, "version", "%{version}")
    add(root, "packaging", "jar")
    props = ET.SubElement(root, tag("properties"))
    add(props, "maven.compiler.release", "11")
    build = ET.SubElement(root, tag("build"))
    add(build, "sourceDirectory", "src")
    resources(build)
    plugins = jar_plugin(build, module_name, main_class)
    compiler = ET.SubElement(plugins, tag("plugin"))
    add(compiler, "groupId", "org.apache.maven.plugins")
    add(compiler, "artifactId", "maven-compiler-plugin")
    add(compiler, "version", "3.12.1")
    configuration = ET.SubElement(compiler, tag("configuration"))
    add(configuration, "release", "11")
    add(configuration, "compilerArgument", "-proc:none")
    if depend_on_args4j:
        deps = ET.SubElement(root, tag("dependencies"))
        dep = ET.SubElement(deps, tag("dependency"))
        add(dep, "groupId", "args4j")
        add(dep, "artifactId", "args4j")
        add(dep, "version", "%{version}")
        # Hidden from builddep. %build -p removes this before Maven runs.
        add(dep, "optional", "true")
    return root

main_java = list(Path("args4j/src").rglob("*.java"))
tools_java = list(Path("args4j-tools/src").rglob("*.java"))
if len(main_java) != 63 or len(tools_java) != 11:
    raise SystemExit("unexpected java file count")

aggregator = ET.Element(tag("project"))
add(aggregator, "modelVersion", "4.0.0")
add(aggregator, "groupId", "args4j")
add(aggregator, "artifactId", "args4j-site")
add(aggregator, "version", "%{version}")
add(aggregator, "packaging", "pom")
modules = ET.SubElement(aggregator, tag("modules"))
add(modules, "module", "args4j")
add(modules, "module", "args4j-tools")
ET.ElementTree(aggregator).write("pom.xml", encoding="utf-8", xml_declaration=True)
ET.ElementTree(project("args4j", "args4j", "", False)).write(
    "args4j/pom.xml", encoding="utf-8", xml_declaration=True)
ET.ElementTree(project("args4j-tools", "args4j.tools", "org.kohsuke.args4j.apt.Main", True)).write(
    "args4j-tools/pom.xml", encoding="utf-8", xml_declaration=True)

text = Path("pom.xml").read_text(encoding="utf-8")
text += Path("args4j/pom.xml").read_text(encoding="utf-8")
text += Path("args4j-tools/pom.xml").read_text(encoding="utf-8")
for needle in (
    "<packaging>pom</packaging>",
    "<module>args4j</module>",
    "<module>args4j-tools</module>",
    "<maven.compiler.release>11</maven.compiler.release>",
    "<Automatic-Module-Name>args4j</Automatic-Module-Name>",
    "<Automatic-Module-Name>args4j.tools</Automatic-Module-Name>",
    "<optional>true</optional>",
):
    if needle not in text:
        raise SystemExit("missing " + needle)
if "<module>args4j-maven-plugin</module>" in text or "<packaging>bundle</packaging>" in text:
    raise SystemExit("plugin module or bundle packaging leaked")
if "maven-bundle-plugin" in text or "maven-assembly-plugin" in text or "org.kohsuke</groupId>" in text:
    raise SystemExit("unwanted plugin leaked")
PY

%build -p
python - <<'PY'
import xml.etree.ElementTree as ET
from pathlib import Path

path = Path("args4j-tools/pom.xml")
ET.register_namespace("", "http://maven.apache.org/POM/4.0.0")
tree = ET.parse(path)
root = tree.getroot()

def local(name):
    return name.rsplit("}", 1)[-1]

removed = 0
for parent in list(root.iter()):
    for child in list(parent):
        if local(child.tag) == "optional":
            parent.remove(child)
            removed += 1
if removed != 1:
    raise SystemExit("expected one optional marker")
tree.write(path, encoding="utf-8", xml_declaration=True)
text = path.read_text(encoding="utf-8")
if "<optional>" in text:
    raise SystemExit("optional marker remains")
if "<artifactId>args4j</artifactId>" not in text:
    raise SystemExit("args4j dependency missing")
PY

%build -a
cat > manifest-addition <<'EOF'
Automatic-Module-Name: args4j
EOF
jar ufm args4j/target/args4j-%{version}.jar manifest-addition
java --module-path args4j/target/args4j-%{version}.jar --describe-module args4j | grep -q '^args4j'
cat > manifest-addition <<'EOF'
Automatic-Module-Name: args4j.tools
EOF
jar ufm args4j-tools/target/args4j-tools-%{version}.jar manifest-addition
java --module-path args4j-tools/target/args4j-tools-%{version}.jar --describe-module args4j.tools | grep -q '^args4j.tools'

%files -f .mfiles
%doc LICENSE
