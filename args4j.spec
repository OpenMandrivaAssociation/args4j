%{?_javapackages_macros:%_javapackages_macros}
Name:              args4j
%global tools_name %{name}-tools
%global site_name  %{name}-site

Version:          2.0.25
Release:          1.0%{?dist}
Summary:          Small Java lib to parse command line options/args in CUI apps
License:          MIT and BSD

# http://args4j.java.net/
URL:              http://%{name}.java.net/
Source0:          https://github.com/kohsuke/%{name}/archive/%{site_name}-%{version}.tar.gz

BuildArch:        noarch

BuildRequires:    java-devel
BuildRequires:    jpackage-utils
BuildRequires:    maven-local
BuildRequires:    maven-dependency-plugin
BuildRequires:    maven-install-plugin
BuildRequires:    maven-shade-plugin
BuildRequires:    mockito

Requires:         java
Requires:         jpackage-utils

%description
args4j is a small Java class library that makes it easy
to parse command line options/arguments in your CUI application.
- It makes the command line parsing very easy by using annotations.
- You can generate the usage screen very easily.
- You can generate HTML/XML that lists all options for your documentation.
- Fully supports localization.
- It is designed to parse javac like options (as opposed to GNU-style
  where ls -lR is considered to have two options l and R.)

args4j-tools are development-time tools for generating additional artifacits.

%package javadoc
Summary:          API documentation for %{name}

Requires:         jpackage-utils

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q -n %{name}-%{site_name}-%{version}

# removing classpath addition
sed -i 's/<addClasspath>true/<addClasspath>false/g' %{tools_name}/pom.xml

# fix ant group id
sed -i 's/<groupId>ant/<groupId>org.apache.ant/g' %{tools_name}/pom.xml

# removing bundled stuff
find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;

%pom_xpath_remove "pom:parent"

%build
mvn-rpmbuild -pl :args4j-site,:args4j,:args4j-tools install javadoc:aggregate

%install
# jars
install -d -m 755 %{buildroot}%{_javadir}
install -p -m 644 %{name}/target/%{name}-%{version}.jar %{buildroot}%{_javadir}/%{name}.jar
install -p -m 644 %{tools_name}/target/%{tools_name}-%{version}.jar %{buildroot}%{_javadir}/%{tools_name}.jar

# pom
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -pm 644 pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{site_name}.pom
install -pm 644 %{name}/pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom
install -pm 644 %{tools_name}/pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{tools_name}.pom

%add_maven_depmap JPP-%{site_name}.pom
%add_maven_depmap JPP-%{name}.pom %{name}.jar
%add_maven_depmap JPP-%{tools_name}.pom %{tools_name}.jar

# javadoc
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -pr target/site/apidocs/* %{buildroot}%{_javadocdir}/%{name}

%files
%doc %{name}/LICENSE.txt
%{_javadir}/%{name}.jar
%{_javadir}/%{tools_name}.jar
%{_mavenpomdir}/JPP-%{site_name}.pom
%{_mavenpomdir}/JPP-%{name}.pom
%{_mavenpomdir}/JPP-%{tools_name}.pom
%{_mavendepmapfragdir}/%{name}

%files javadoc
%doc %{name}/LICENSE.txt
%doc %{_javadocdir}/%{name}

%changelog
* Sat Aug 10 2013 Mat Booth <fedora@matbooth.co.uk> - 2.0.25-1
- Update to latest upstream, fixes #981339

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.23-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jun 27 2013 Mat Booth <fedora@matbooth.co.uk> - 2.0.23-1
- Update to latest upstream, fixes #808703
- Also drop unneeded patches

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.16-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 2.0.16-10
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Thu Dec 13 2012 Roland Grunberg <rgrunber@redhat.com> - 2.0.16-9
- Update to conform with latest Java packaging guidelines.

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.16-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jan 31 2012 Ville Skyttä <ville.skytta@iki.fi> - 2.0.16-7
- Apply upstream source encoding patch to fix build with java 1.7.

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.16-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Jun 13 2011 Jaromir Capik <jcapik@redhat.com> - 2.0.16-4
- OSGi metadata generated

* Mon May 30 2011 Jaromir Capik <jcapik@redhat.com> - 2.0.16-3
- Removal of bundled stuff in args4j/lib

* Wed May 25 2011 Jaromir Capik <jcapik@redhat.com> - 2.0.16-2
- Removal of unused ant dependency

* Tue May 24 2011 Jaromir Capik <jcapik@redhat.com> - 2.0.16-1
- Initial version of the package
