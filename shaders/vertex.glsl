#version 330 core

layout (location = 0) in vec2 vert;
layout (location = 1) in vec2 texcoord;

out vec2 fragmentTexCoord;

void main()
{
    fragmentTexCoord = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}