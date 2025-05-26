preset_dependencies_analysis = """{
  "inferred_project_type": {
    "project_type": "Spring Boot application",
    "language": "Java",
    "framework": "Spring Boot",
    "java_version": "17",
    "build_tool": "Maven"
  },
  "dependencies": {
    "third_party": [
      {
        "groupId": "com.baomidou",
        "artifactId": "mybatis-plus-boot-starter",
        "version": "3.5.3.1"
      },
      {
        "groupId": "com.github.xiaoymin",
        "artifactId": "knife4j-openapi3-jakarta-spring-boot-starter",
        "version": "4.1.0"
      },
      {
        "groupId": "io.jsonwebtoken",
        "artifactId": "jjwt-api",
        "version": "0.11.2"
      },
      {
        "groupId": "io.jsonwebtoken",
        "artifactId": "jjwt-impl",
        "version": "0.11.2",
        "scope": "runtime"
      },
      {
        "groupId": "io.jsonwebtoken",
        "artifactId": "jjwt-jackson",
        "version": "0.11.2",
        "scope": "runtime"
      },
      {
        "groupId": "com.github.whvcse",
        "artifactId": "easy-captcha",
        "version": "1.6.2"
      },
      {
        "groupId": "io.minio",
        "artifactId": "minio",
        "version": "8.2.0"
      },
      {
        "groupId": "com.aliyun",
        "artifactId": "dysmsapi20170525",
        "version": "2.0.23"
      },
      {
        "groupId": "com.mysql",
        "artifactId": "mysql-connector-j"
      },
      {
        "groupId": "org.projectlombok",
        "artifactId": "lombok"
      },
      {
        "groupId": "commons-codec",
        "artifactId": "commons-codec",
        "version": "1.11"
      },
      {
        "groupId": "org.springframework.boot",
        "artifactId": "spring-boot-starter-web"
      },
      {
        "groupId": "org.springframework.boot",
        "artifactId": "spring-boot-starter-data-redis"
      },
      {
        "groupId": "org.springframework.boot",
        "artifactId": "spring-boot-starter-test",
        "scope": "test"
      }
    ],
    "runtime": {
      "java_version": "17"
    },
    "external_services": {
      "databases": ["MySQL"],
      "message_queues": [],
      "caches": ["Redis"],
      "object_storages": ["MinIO"],
      "others": []
    }
  }
}"""

preset_service_inference = """"
```
{
  "databases": [
    {
      "type": "MySQL",
      "version": "not specified",
      "connection_parameters": {
        "host": "192.168.230.101",
        "port": 3306,
        "database_name": "lease",
        "username": "root",
        "password": "Norknown2@",
        "connection_timeout": 60000,
        "idle_timeout": 500000,
        "max_lifetime": 540000,
        "maximum_pool_size": 12,
        "minimum_idle": 10,
        "connection_test_query": "SELECT 1"
      }
    }
  ],
  "message_queues": [],
  "caches": [
    {
      "type": "Redis",
      "version": "not specified",
      "connection_parameters": {
        "host": "192.168.230.101",
        "port": 6379,
        "database": 0
      }
    }
  ],
  "object_storage": [
    {
      "type": "MinIO",
      "version": "not specified",
      "connection_parameters": {
        "endpoint": "http://192.168.230.101:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "bucket_name": "lease"
      }
    }
  ],
  "aliyun_sms": {
    "access_key_id": "aaa1133dddddddnnnnfdaAAA",
    "access_key_secret": "bbbddd1133aaa",
    "endpoint": "dysmsapi.aliyuncs.com"
  },
  "runtime_environment": {
    "java_version": "17"
  }
}
```

This structured information captures the types of services used in your project along with their respective configuration details—ready for integration into deployment workflows.
"""