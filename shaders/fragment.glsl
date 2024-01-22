#version 330 core

uniform sampler2D tex;
uniform vec3 colour_correction;

out vec4 color;
in vec2 fragmentTexCoord;

void main() {
    color = vec4(texture(tex, fragmentTexCoord).rgb, 1.0);
    color = vec4(color.r * colour_correction.x, color.g * colour_correction.y, color.b * colour_correction.z, 1.0);
}