#include <string>
#include <iostream>
#include <sstream>
#include <cassert>
#include <cstdlib>
#include <cstring>

#include "service.h"
#include "proc-service.h"
//#include "load-service.h"

std::string test_service_dir;

void init_test_service_dir()
{
    test_service_dir = "./test-services";
}

void test_basic()
{
    dirload_service_set sset(test_service_dir.c_str());
    auto t1 = sset.load_service("t1");
    assert(t1->get_name() == "t1");
}

void test_env_subst()
{
    dirload_service_set sset(test_service_dir.c_str());
    setenv("ONEVAR", "a", true);
    setenv("TWOVAR", "hellohello", true);
    // leave THREEVAR undefined
    auto t2 = static_cast<base_process_service *>(sset.load_service("t2"));
    auto exec_parts = t2->get_exec_arg_parts();
    assert(strcmp("echo", exec_parts[0]) == 0);
    assert(strcmp("a", exec_parts[1]) == 0);
    assert(strcmp("hellohello", exec_parts[2]) == 0);
    assert(strcmp("", exec_parts[3]) == 0);
}

void test_nonexistent()
{
    bool got_service_not_found = false;
    dirload_service_set sset(test_service_dir.c_str());
    try {
        sset.load_service("does-not-exist");
    }
    catch (service_not_found &) {
        got_service_not_found = true;
    }
    assert(got_service_not_found);
}

void test_settings()
{
    using string = std::string;
    using string_iterator = std::string::iterator;

    // prelim_dep: A preliminary (unresolved) service dependency
    class prelim_dep
    {
        public:
        std::string name;
        dependency_type dep_type;

        prelim_dep(const std::string &name_p, dependency_type dep_type_p)
            : name(name_p), dep_type(dep_type_p) { }
        prelim_dep(std::string &&name_p, dependency_type dep_type_p)
            : name(std::move(name_p)), dep_type(dep_type_p) { }
    };

    dinit_load::service_settings_wrapper<prelim_dep> settings;

    std::stringstream ss;

    ss << "type = process\n"
            "command = /something/test\n"
            "depends-on = abc\n"
            "rlimit-nofile = 50:100\n"
            "rlimit-core = 60:\n"
            "rlimit-data = -:-";

    try {
        process_service_file("test-service", ss,
                [&](string &line, string &setting, string_iterator &i, string_iterator &end) -> void {

            auto process_dep_dir_n = [&](std::list<prelim_dep> &deplist, const std::string &waitsford,
                    dependency_type dep_type) -> void {
                //process_dep_dir(name.c_str(), service_filename, deplist, waitsford, dep_type);
            };

            auto load_service_n = [&](const string &dep_name) -> const string & {
                return dep_name;
            };

            try {
                process_service_line(settings, "test-service", line, setting, i, end, load_service_n, process_dep_dir_n);
            }
            catch (service_description_exc &exc) {
                //report_service_description_exc(exc);
            }
        });
    }
    catch (std::system_error &sys_err)
    {
        //report_error(sys_err, name);
        throw service_description_exc("", "error while reading service description.");
    }

    assert(settings.service_type == service_type_t::PROCESS);
    assert(settings.command == "/something/test");
    assert(settings.rlimits.size() == 3);

    assert(settings.rlimits[0].resource_id == RLIMIT_NOFILE);
    assert(settings.rlimits[0].soft_set && settings.rlimits[0].hard_set);
    assert(settings.rlimits[0].limits.rlim_cur == 50);
    assert(settings.rlimits[0].limits.rlim_max == 100);

    assert(settings.rlimits[1].resource_id == RLIMIT_CORE);
    assert(settings.rlimits[1].soft_set && !settings.rlimits[1].hard_set);
    assert(settings.rlimits[1].limits.rlim_cur == 60);

    assert(settings.rlimits[2].resource_id == RLIMIT_DATA);
    assert(settings.rlimits[2].soft_set && settings.rlimits[2].hard_set);
    assert(settings.rlimits[2].limits.rlim_cur == RLIM_INFINITY);
    assert(settings.rlimits[2].limits.rlim_max == RLIM_INFINITY);

    assert(settings.depends.size() == 1);
    assert(settings.depends.front().dep_type == dependency_type::REGULAR);
    assert(settings.depends.front().name == "abc");
}


#define RUN_TEST(name, spacing) \
    std::cout << #name "..." spacing << std::flush; \
    name(); \
    std::cout << "PASSED" << std::endl;

int main(int argc, char **argv)
{
    init_test_service_dir();
    RUN_TEST(test_basic, "                ");
    RUN_TEST(test_env_subst, "            ");
    RUN_TEST(test_nonexistent, "          ");
    RUN_TEST(test_settings, "             ");
    return 0;
}
