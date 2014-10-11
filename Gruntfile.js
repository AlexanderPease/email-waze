'use strict';

module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      options: {
        mangle: true,
        sourceMap: true,
        sourceMapName: 'scripts/js/main.map'
      },
      target: {
        files: {
          'scripts/js/main.min.js': ['scripts/js/main.js']
        }
      }
    },
    jshint: {
      options: {
        reporter: require('jshint-stylish')
      },
      all: ['scripts/js/main.js']
    },
    compass: {
      options: {
        sassDir: 'sass',
        cssDir: 'static/css',
        sourcemap: true,
        noLineComments: true,
        debugInfo: false,
        outputStyle: 'compressed'
      },
      dist: {}
    },
    cacheBust: {
      options: {
        encoding: 'utf8',
        algorithm: 'md5',
        length: 16,
        rename: false
      },
      assets: {
        files: [{
          src: ['templates/base.html']
        }]
      }
    },
    watch: {
      files: ['sass/*'],
      tasks: ['compass']
    }
  });

  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-compass');
  grunt.loadNpmTasks('grunt-cache-bust');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');

  grunt.registerTask('default', ['jshint']);
  grunt.registerTask('compile', ['compass', 'uglify']);

};
